param searchServiceName string  
param location string = resourceGroup().location

param sku object = {
  name: 'standard'
}

param semanticSearch string = 'disabled'

resource searchService 'Microsoft.Search/searchServices@2021-04-01-preview' = {
  name: searchServiceName
  location: location  
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    hostingMode: 'default'
    partitionCount: 1
    publicNetworkAccess: 'Enabled'
    replicaCount: 1
    semanticSearch: semanticSearch
  }
  sku: sku
}

output searchServiceId string = searchService.id
output searchServiceEndpoint string = 'https://${searchServiceName}.search.windows.net/'
output searchServiceName string = searchService.name
