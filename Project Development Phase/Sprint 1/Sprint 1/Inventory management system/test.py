import base64
class code:
    def encode(data):
        encode = data.encode("utf-8")
        return base64.b16encode(encode)

    def decode(data):
        return base64.b16decode(data).decode("utf-8")

#a = code.encode('srijith')
#print(a)
a='7372696A697468723240676D61696C2E636F6D'
#print(code.decode(f"{a}"))
print(code.decode(f"{a}"))
#print("7372696A697468723240676D61696C2E636F6D")
#a="b'7372696A697468723240676D61696C2E636F6D'"
#res = ''.join(filter(lambda i: i.isdigit(), a))
#print(res)

print(a.encode(encoding='utf8'))
