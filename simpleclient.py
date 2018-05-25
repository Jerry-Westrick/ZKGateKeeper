
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
An example client. Run simpleserv.py first before running this.
"""
from __future__ import print_function

from struct import pack, unpack, unpack_from

from twisted.internet import reactor, protocol


# a client protocol




class ZKClientProtocol(protocol.Protocol):
    """Once connected, send a message, then print the result."""
    replyId = 0
    sessionId = 0
    commands = {
        # Comandos generales.
        'CONNECT': 0x03e8,
        'DISCONNECT': 0x03e9,
        'ENABLE_DEVICE': 0x03ea,
        'DISABLE_DEVICE': 0x03eb,
        'UNLOCK_DOOR': 0x001f,
        'ENABLE_EVENTS': 0x01f4,

        # Comandos de respuesta.
        'ACK_OK': 0x07d0,
        'ACK_ERROR': 0x07d1
    }


    def checksum(self, buffer):
        """calculate check sum"""
        checksum = 0
        buffersize = len(buffer)
        for i in range(0, buffersize, 2):
            if i == buffersize - 1:
                checksum += buffersize[i]
            else:
                x = unpack_from('!H', buffer, i)[0]
                checksum += x
        return checksum

    def connectionMade(self):
        print("Connection Made...")
        self.sendMessage(self.commands['UNLOCK_DOOR'], pack('!HH', 10, 0))

    
    def dataReceived(self, data):
        """Parse Response """
        print(data)

    def connectionLost(self, reason):
        print("connection lost")

    def sendMessage(self, cmd, msg):
        """this i a comment"""
        #todo cmd is a constant...
        #todo Get session Id in connect

        reply_id = 0

        if cmd not in [self.commands['CONNECT'], self.commands['ACK_OK']]:
            self.replyId += 1
            reply_id = self.replyId

        # Build data_buff to calculate checksum
        data_buf = pack('!HHHH', cmd, 0, self.sessionId, reply_id) + msg
        chksums = self.checksum(data_buf)

        # Build Buffer to be sent
        send_buf = pack('!IIHHHH', 0x5050827d, len(msg) + 16, cmd, chksums, self.sessionId, self.replyId)
        send_buf += msg
        self.transport.write(send_buf)

        return



class ZKClientFactory(protocol.ClientFactory):
    protocol = ZKClientProtocol

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()


# this connects the protocol to a server running on port 8000
def main():
    f = ZKClientFactory()
    reactor.connectTCP("10.0.0.12", 4370, f)
    reactor.run()


# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
