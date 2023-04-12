param storageAccountName string  
param location string = resourceGroup().location  

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {  
  name: storageAccountName  
  location: location  
  kind: 'StorageV2'  
  sku: {  
    name: 'Standard_LRS'  
  }  
}


output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name
