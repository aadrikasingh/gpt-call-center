param openAIName string
param location string = resourceGroup().location

param deployments array = []

resource openAIService 'Microsoft.CognitiveServices/accounts@2022-10-01' = {
  name: openAIName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAIName
    publicNetworkAccess: 'Enabled'
  }
}

@batchSize(1)
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2022-10-01' = [for deployment in deployments: {
  parent: openAIService
  name: deployment.name
  properties: {
    model: deployment.model
    raiPolicyName: contains(deployment, 'raiPolicyName') ? deployment.raiPolicyName : null
    scaleSettings: {
      scaleType: 'Standard'
    }
  }
}]

output openAIServiceId string = openAIService.id
output openAIServiceEndpoint string = 'https://${openAIName}.search.windows.net/'
output openAIServiceName string = openAIService.name
