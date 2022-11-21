import requests
import pywaves as pw

class Contract(object):

    def __init__(self, contractAddress, seed, pywaves=pw):
        self.pw = pywaves
        self.contractAddress = contractAddress

        metaInfo = self.parseContractAddress()
        extractedMethods = metaInfo.keys()
        for method in extractedMethods:
            signature = self.generateCode(method, metaInfo[method], seed)
            exec(signature, globals())
            setattr(self, method, eval(method))


    def parseContractAddress(self):
        metaInfo = requests.get(self.pw.NODE + '/addresses/scriptInfo/' + self.contractAddress + '/meta').json()

        return metaInfo['meta']['callableFuncTypes']

    def generateCode(self, method, parameters, seed):
        parameterList = ''
        callParameters = 'parameters = [\n'

        for parameter in parameters:  # doesn't work with keys in vires contract

            if parameter["name"] == "from":  # patch for keyword from in claimProtocolProfitFrom in vires contract
                par_name = "from_1"
            else:
                par_name = parameter["name"]

            parameterList += par_name + ', '
            type = parameter["type"]

            if type == 'Int':
                callParameters += '\t\t{ "type": "integer", "value": ' + par_name + ' },\n'
            elif type == 'String':
                callParameters += '\t\t{ "type": "string", "value": ' + par_name + ' },\n'
            elif type == 'Boolean':
                callParameters += '\t\t{ "type": "boolean", "value": ' + par_name + ' },\n'

        if len(parameters) > 0:
            callParameters = callParameters[0:len(callParameters) - 2] + '\n'
        callParameters += '\t]'
        call = 'return pw.Address(seed = \'' + seed + '\').invokeScript(\'' + self.contractAddress + '\', \'' + method + '\', parameters, [])'

        code = 'def ' + method + '(' + parameterList[0: len(parameterList) - 2] + '):\n\t' + callParameters + '\n\t' + call

        return code
