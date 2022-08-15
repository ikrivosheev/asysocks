import ssl
import asyncio
from asysocks.unicomm.common.packetizers.base import Packetizer
from asysocks.unicomm.common.packetizers.ssl import PacketizerSSL

class UniConnection:
	def __init__(self, reader:asyncio.StreamReader, writer:asyncio.StreamWriter, packetizer:Packetizer):
		self.reader = reader
		self.writer = writer
		self.packetizer = packetizer
		self.packetizer_task = None
		self.closing = False

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc, tb):
		await self.close()

	def get_peer_certificate(self):
		return self.packetizer.get_peer_certificate()
	
	def change_packetizer(self, packetizer):
		rem_data = self.packetizer.flush_buffer()
		if isinstance(self.packetizer, PacketizerSSL):
			self.packetizer.packetizer = packetizer
		else:
			self.packetizer = packetizer
		
	
	def packetizer_control(self, *args, **kw):
		return self.packetizer.packetizer_control(*args, **kw)

	async def wrap_ssl(self, ssl_ctx = None, packetizer = None):
		if packetizer is None:
			packetizer = self.packetizer
		if ssl_ctx is None:
			ssl_ctx = ssl.create_default_context()
			ssl_ctx.check_hostname = False
			ssl_ctx.verify_mode = ssl.CERT_NONE
		self.packetizer = PacketizerSSL(ssl_ctx, packetizer)
		await self.packetizer.do_handshake(self.reader, self.writer)

	async def close(self):
		self.closing = True
		self.writer.close()

	async def write(self, data):
		async for packet in self.packetizer.data_out(data):
			self.writer.write(packet)
			await self.writer.drain()

	async def read_one(self):
		async for packet in self.read():
			return packet

	async def read(self):
		data = None
		while self.closing is False:
			if data is not None:	
				async for result in self.packetizer.data_in(data):
					yield result
				data = None
			else:
				data = await self.reader.read(self.packetizer.buffer_size)
				if data == b'':
					break