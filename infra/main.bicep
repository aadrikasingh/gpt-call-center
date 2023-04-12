targetScope = 'subscription'

param resourceGroupName string
param storageAccountName string
param speechServiceName string
param searchServiceName string
param location string
param openAIServiceName string

@description('Id of the user or app to assign application roles')
param principalId string

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {  
  name: resourceGroupName  
  location: location
}  

module storageAccount 'core/storage/storage-account.bicep' = {  
  name: 'storageAccountModule'  
  scope: resourceGroup
  params: {  
    storageAccountName: storageAccountName
    location: location
  }  
}

module speechService 'core/speech/speech-services.bicep' = {  
  name: 'speechServiceModule'  
  scope: resourceGroup
  params: {  
    speechServiceName: speechServiceName  
    location: location
  }  
}

module searchService 'core/search/search-services.bicep' = {  
  name: 'searchServiceModule'  
  scope: resourceGroup
  params: {  
    searchServiceName: searchServiceName  
    location: location
  }  
}

module openAIService 'core/openAI/open-ai-services.bicep' = {
  name: 'openAIModule'
  scope: resourceGroup
  params: {
    openAIName: openAIServiceName
    location: location
    deployments: [
      {
        name: 'gpt-4-32k'
        model: {
          format: 'OpenAI'
          name: 'gpt-4-32k'
          version: '0314'
        }
        scaleSettings: {
          scaleType: 'Standard'
        }
      }
      {
        name: 'text-embedding-ada-002'
        model: {
          format: 'OpenAI'
          name: 'text-embedding-ada-002'
          version: '2'
        }
        scaleSettings: {
          scaleType: 'Standard'
        }
      }
      {
        name: 'gpt-35-turbo'
        model: {
          format: 'OpenAI'
          name: 'gpt-35-turbo'
          version: '0301'
        }
        scaleSettings: {
          scaleType: 'Standard'
        }
      }
    ]
  }
}

module storageRoleUser 'core/security/role.bicep' = {
  scope: resourceGroup
  name: 'storage-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
    principalType: 'User'
  }
}

module storageContribRoleUser 'core/security/role.bicep' = {
  scope: resourceGroup
  name: 'storage-contribrole-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    principalType: 'User'
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_OPENAI_SERVICE string = openAIService.outputs.openAIServiceName
output AZURE_OPENAI_ENDPOINT string = openAIService.outputs.openAIServiceEndpoint

output AZURE_SEARCH_SERVICE string = searchService.outputs.searchServiceName
output AZURE_SEARCH_ENDPOINT string = searchService.outputs.searchServiceEndpoint

output AZURE_STORAGE_ACCOUNT string = storageAccount.outputs.storageAccountName
