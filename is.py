from zeep import Client

client = Client('tests/wsdl_files/example.rst')
client.service.ping()