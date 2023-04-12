param speechServiceName string  
param location string = resourceGroup().location  
param speechServiceSku string = 'S0'

resource speechService 'Microsoft.CognitiveServices/accounts@2021-04-30' = {  
  name: speechServiceName  
  location: location  
  kind: 'SpeechServices'  
  sku: {  
    name: speechServiceSku  
  }  
  properties: {  
    customSubDomainName: speechServiceName  
  }  
}

output searchServiceId string = speechService.id
output searchServiceEndpoint string = 'https://${speechServiceName}.cognitiveservices.azure.com/sts/v1.0/issuetoken'
output searchServiceName string = speechService.name
