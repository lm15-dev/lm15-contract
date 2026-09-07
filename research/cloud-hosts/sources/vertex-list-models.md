Home

          Documentation

          AI and ML

          Gemini Enterprise Agent Platform

    Send feedback

      Agent Platform API

      Stay organized with collections

      Save and categorize content based on your preferences.

      The Agent Platform API lets you manage Agent Platform resources in Google Cloud.

        Service: aiplatform.googleapis.com

        To call this service, we recommend that you use the Google-provided client libraries. If your application needs to use your own libraries to call this service, use the following information when you make the API requests.

          Discovery document

          A Discovery Document is a machine-readable specification for describing and consuming REST APIs. It is used to build client libraries, IDE plugins, and other tools that interact with Google APIs. One service may provide multiple discovery documents. This service provides the following discovery documents:

            https://aiplatform.googleapis.com/$discovery/rest?version=v1

            https://aiplatform.googleapis.com/$discovery/rest?version=v1beta1

          Service endpoint

A service endpoint is a base URL that specifies the network address of an API service. One service might have multiple service endpoints. This service has the following service endpoints and all URIs below are relative to these service endpoints:

            https://aiplatform.googleapis.com

            https://africa-south1-aiplatform.googleapis.com

            https://asia-east1-aiplatform.googleapis.com

            https://asia-east2-aiplatform.googleapis.com

            https://asia-northeast1-aiplatform.googleapis.com

            https://asia-northeast2-aiplatform.googleapis.com

            https://asia-northeast3-aiplatform.googleapis.com

            https://asia-south1-aiplatform.googleapis.com

            https://asia-southeast1-aiplatform.googleapis.com

            https://asia-southeast2-aiplatform.googleapis.com

            https://australia-southeast1-aiplatform.googleapis.com

            https://australia-southeast2-aiplatform.googleapis.com

            https://europe-central2-aiplatform.googleapis.com

            https://europe-north1-aiplatform.googleapis.com

            https://europe-southwest1-aiplatform.googleapis.com

            https://europe-west1-aiplatform.googleapis.com

            https://europe-west2-aiplatform.googleapis.com

            https://europe-west3-aiplatform.googleapis.com

            https://europe-west4-aiplatform.googleapis.com

            https://europe-west6-aiplatform.googleapis.com

            https://europe-west8-aiplatform.googleapis.com

            https://europe-west9-aiplatform.googleapis.com

            https://europe-west12-aiplatform.googleapis.com

            https://me-central1-aiplatform.googleapis.com

            https://me-central2-aiplatform.googleapis.com

            https://me-west1-aiplatform.googleapis.com

            https://northamerica-northeast1-aiplatform.googleapis.com

            https://northamerica-northeast2-aiplatform.googleapis.com

            https://southamerica-east1-aiplatform.googleapis.com

            https://southamerica-west1-aiplatform.googleapis.com

            https://us-central1-aiplatform.googleapis.com

            https://us-east1-aiplatform.googleapis.com

            https://us-east4-aiplatform.googleapis.com

            https://us-south1-aiplatform.googleapis.com

            https://us-west1-aiplatform.googleapis.com

            https://us-west2-aiplatform.googleapis.com

            https://us-west3-aiplatform.googleapis.com

            https://us-west4-aiplatform.googleapis.com

            https://us-east5-aiplatform.googleapis.com

            See Feature
            availability for the supported machine learning features for each region.

        REST Resource: reasoningEngines.v1.projects.locations.reasoningEngines.api

                Methods

                  invokeReasoningEngine

                  POST /reasoningEngines/v1/{name}/api/**

                  Invokes reasoning engine with arbitrary HTTP requests for both unary and server-side streaming cases.

        REST Resource: reasoningEngines.v1.projects.locations.reasoningEngines.runtimeRevisions.api

                Methods

                  invokeReasoningEngine

                  PATCH /reasoningEngines/v1/{name}/api/**

                  Invokes reasoning engine with arbitrary HTTP requests for both unary and server-side streaming cases.

        REST Resource: reasoningEngines.v1beta1.projects.locations.reasoningEngines.api

                Methods

                  invokeReasoningEngine

                  POST /reasoningEngines/v1beta1/{name}/api/**

                  Invokes reasoning engine with arbitrary HTTP requests for both unary and server-side streaming cases.

        REST Resource: reasoningEngines.v1beta1.projects.locations.reasoningEngines.runtimeRevisions.api

                Methods

                  invokeReasoningEngine

                  PATCH /reasoningEngines/v1beta1/{name}/api/**

                  Invokes reasoning engine with arbitrary HTTP requests for both unary and server-side streaming cases.

        REST Resource: reasoningEngines.ws.v1.projects.locations.reasoningEngines.api

                Methods

                  bidiInvokeReasoningEngine

                  GET /reasoningEngines/ws/v1/{name}/api/**

                  Invokes reasoning engine with arbitrary WebSocket requests for bidi streaming

        REST Resource: reasoningEngines.ws.v1.projects.locations.reasoningEngines.revisions.runtimeRevisions.api

                Methods

                  bidiInvokeReasoningEngine

                  POST /reasoningEngines/ws/v1/{name}/api/**

                  Invokes reasoning engine with arbitrary WebSocket requests for bidi streaming

        REST Resource: reasoningEngines.ws.v1beta1.projects.locations.reasoningEngines.api

                Methods

                  bidiInvokeReasoningEngine

                  GET /reasoningEngines/ws/v1beta1/{name}/api/**

                  Invokes reasoning engine with arbitrary WebSocket requests for bidi streaming

        REST Resource: reasoningEngines.ws.v1beta1.projects.locations.reasoningEngines.revisions.runtimeRevisions.api

                Methods

                  bidiInvokeReasoningEngine

                  POST /reasoningEngines/ws/v1beta1/{name}/api/**

                  Invokes reasoning engine with arbitrary WebSocket requests for bidi streaming

        REST Resource: v1.media

                Methods

                  upload

                  POST /v1/{parent}/ragFiles:upload

                  POST /upload/v1/{parent}/ragFiles:upload

                  Upload a file into a RagCorpus.

        REST Resource: v1.operations

                Methods

                  cancel

                  POST /v1/{name}:cancel

                  Starts asynchronous cancellation on a long-running operation.

                  delete

                  DELETE /v1/{name}

                  Deletes a long-running operation.

                  get

                  GET /v1/{name}

                  Gets the latest state of a long-running operation.

                  list

                  GET /v1/operations

                  Lists operations that match the specified filter in the request.

                  wait

                  POST /v1/{name}:wait

                  Waits until the specified long-running operation is done or reaches at most a specified timeout, returning the latest state.

        REST Resource: v1.projects.locations

                Methods

                  askContexts

                  POST /v1/{parent}:askContexts

                  Agentic Retrieval Ask API for RAG.

                  asyncRetrieveContexts

                  POST /v1/{parent}:asyncRetrieveContexts

                  Asynchronous API to retrieves relevant contexts for a query.

                  augmentPrompt

                  POST /v1/{parent}:augmentPrompt

                  Given an input prompt, it returns augmented prompt from vertex rag store  to guide LLM towards generating grounded responses.

                  corroborateContent

                  POST /v1/{parent}:corroborateContent

                  Given an input text, it returns a score that evaluates the factuality of the text.

                  deploy

                  POST /v1/{destination}:deploy

                  Deploys a model to a new endpoint.

                  evaluateInstances

                  POST /v1/{location}:evaluateInstances

                  Evaluates instances based on a given metric.

                  generateSyntheticData

                  POST /v1/{location}:generateSyntheticData

                  Generates synthetic (artificial) data based on a description

                  getRagEngineConfig

                  GET /v1/{name}

                  Gets a RagEngineConfig.

                  getSemanticGovernancePolicyEngine

                  GET /v1/{name}

                  Gets a SemanticGovernancePolicyEngine.

                  retrieveContexts

                  POST /v1/{parent}:retrieveContexts

                  Retrieves relevant contexts for a query.

                  updateRagEngineConfig

                  PATCH /v1/{ragEngineConfig.name}

                  Updates a RagEngineConfig.

                  updateSemanticGovernancePolicyEngine

                  PATCH /v1/{semanticGovernancePolicyEngine.name}

                  Updates a SemanticGovernancePolicyEngine.

        REST Resource: v1.projects.locations.batchPredictionJobs

                Methods

                  cancel

                  POST /v1/{name}:cancel

                  Cancels a BatchPredictionJob.

                  create

                  POST /v1/{parent}/batchPredictionJobs

                  Creates a BatchPredictionJob.

                  delete

                  DELETE /v1/{name}

                  Deletes a BatchPredictionJob.

                  get

                  GET /v1/{name}

                  Gets a BatchPredictionJob

                  list

                  GET /v1/{parent}/batchPredictionJobs

                  Lists BatchPredictionJobs in a Location.

        REST Resource: v1.projects.locations.cachedContents

                Methods

                  create

                  POST /v1/{parent}/cachedContents

                  Creates cached content, this call will initialize the cached content in the data storage, and users need to pay for the cache data storage.

                  delete

                  DELETE /v1/{name}

                  Deletes cached content

                  get

                  GET /v1/{name}

                  Gets cached content configurations

                  list

                  GET /v1/{parent}/cachedContents

                  Lists cached contents in a project

                  patch

                  PATCH /v1/{cachedContent.name}

                  Updates cached content configurations

        REST Resource: v1.projects.locations.customJobs

                Methods

                  cancel

                  POST /v1/{name}:cancel

                  Cancels a CustomJob.

                  create

                  POST /v1/{parent}/customJobs

                  Creates a CustomJob.

                  delete

                  DELETE /v1/{name}

                  Deletes a CustomJob.

                  get

                  GET /v1/{name}

                  Gets a CustomJob.

                  list

                  GET /v1/{parent}/customJobs

                  Lists CustomJobs in a Location.

        REST Resource: v1.projects.locations.datasets

                Methods

                  create

                  POST /v1/{parent}/datasets

                  Creates a Dataset.

                  delete

                  DELETE /v1/{name}

                  Deletes a Dataset.

                  export

                  POST /v1/{name}:export

                  Exports data from a Dataset.

                  get

                  GET /v1/{name}

                  Gets a Dataset.

                  import

                  POST /v1/{name}:import

                  Imports data into a Dataset.

                  list

                  GET /v1/{parent}/datasets

                  Lists Datasets in a Location.

                  patch

                  PATCH /v1/{dataset.name}

                  Updates a Dataset.

                  searchDataItems

                  GET /v1/{dataset}:searchDataItems

                  Searches DataItems in a Dataset.

        REST Resource: v1.projects.locations.datasets.annotationSpecs

                Methods

                  get

                  GET /v1/{name}

                  Gets an AnnotationSpec.

        REST Resource: v1.projects.locations.datasets.dataItems

                Methods

                  list

                  GET /v1/{parent}/dataItems

                  Lists DataItems in a Dataset.

        REST Resource: v1.projects.locations.datasets.dataItems.annotations

                Methods

                  list

                  GET /v1/{parent}/annotations

                  Lists Annotations belongs to a dataitem.

        REST Resource: v1.projects.locations.datasets.datasetVersions

                Methods

                  create

                  POST /v1/{parent}/datasetVersions

                  Create a version from a Dataset.

                  delete

                  DELETE /v1/{name}

                  Deletes a Dataset version.

                  get

                  GET /v1/{name}

                  Gets a Dataset version.

                  list

                  GET /v1/{parent}/datasetVersions

                  Lists DatasetVersions in a Dataset.

                  patch

                  PATCH /v1/{datasetVersion.name}

                  Updates a DatasetVersion.

                  restore

                  GET /v1/{name}:restore

                  Restores a dataset version.

        REST Resource: v1.projects.locations.datasets.savedQueries

                Methods

                  delete

                  DELETE /v1/{name}

                  Deletes a SavedQuery.

                  list

                  GET /v1/{parent}/savedQueries

                  Lists SavedQueries in a Dataset.

        REST Resource: v1.projects.locations.deploymentResourcePools

                Methods

                  create

                  POST /v1/{parent}/deploymentResourcePools

                  Create a DeploymentResourcePool.

                  delete

                  DELETE /v1/{name}

                  Delete a DeploymentResourcePool.

                  get

                  GET /v1/{name}

                  Get a DeploymentResourcePool.

                  list

                  GET /v1/{parent}/deploymentResourcePools

                  List DeploymentResourcePools in a location.

                  patch

                  PATCH /v1/{deploymentResourcePool.name}

                  Update a DeploymentResourcePool.

                  queryDeployedModels

                  GET /v1/{deploymentResourcePool}:queryDeployedModels

                  List DeployedModels that have been deployed on this DeploymentResourcePool.

        REST Resource: v1.projects.locations.endpoints

                Methods

                  computeTokens

                  POST /v1/{endpoint}:computeTokens

                  Return a list of tokens based on the input text.

                  countTokens

                  POST /v1/{endpoint}:countTokens

                  Perform a token counting.

                  create

                  POST /v1/{parent}/endpoints

                  Creates an Endpoint.

                  delete

                  DELETE /v1/{name}

                  Deletes an Endpoint.

                  deployModel

                  POST /v1/{endpoint}:deployModel

                  Deploys a Model into this Endpoint, creating a DeployedModel within it.

                  directPredict

                  POST /v1/{endpoint}:directPredict

                  Perform an unary online prediction request to a gRPC model server for Vertex first-party products and frameworks.

                  directRawPredict

                  POST /v1/{endpoint}:directRawPredict

                  Perform an unary online prediction request to a gRPC model server for custom containers.

                  explain

                  POST /v1/{endpoint}:explain

                  Perform an online explanation.

                  generateContent

                  POST /v1/{model}:generateContent

                  Generate content with multimodal inputs.

                  get

                  GET /v1/{name}

                  Gets an Endpoint.

                  list

                  GET /v1/{parent}/endpoints

                  Lists Endpoints in a Location.

                  mutateDeployedModel

                  POST /v1/{endpoint}:mutateDeployedModel

                  Updates an existing deployed model.

                  patch

                  PATCH /v1/{endpoint.name}

                  Updates an Endpoint.

                  predict

                  POST /v1/{endpoint}:predict

                  Perform an online inference.

                  rawPredict

                  POST /v1/{endpoint}:rawPredict

                  Perform an online prediction with an arbitrary HTTP payload.

                  serverStreamingPredict

                  POST /v1/{endpoint}:serverStreamingPredict

                  Perform a server-side streaming online prediction request for Vertex LLM streaming.

                  streamGenerateContent

                  POST /v1/{model}:streamGenerateContent

                  Generate content with multimodal inputs with streaming support.

                  streamRawPredict

                  POST /v1/{endpoint}:streamRawPredict

                  Perform a streaming online prediction with an arbitrary HTTP payload.

                  undeployModel

                  POST /v1/{endpoint}:undeployModel

                  Undeploys a Model from an Endpoint, removing a DeployedModel from it, and freeing all resources it's using.

                  update

                  POST /v1/{endpoint.name}:update

                  Updates an Endpoint with a long running operation.

        REST Resource: v1.projects.locations.endpoints.responses

                Methods

                  delete

                  DELETE /v1/{name}

                  Deletes the response from the endpoint.

                  get

                  GET /v1/{name}

                  Gets the response from the endpoint.

        REST Resource: v1.projects.locations.featureGroups

                Methods

                  create

                  POST /v1/{parent}/featureGroups

                  Creates a new FeatureGroup in a given project and location.

                  delete

                  DELETE /v1/{name}

                  Deletes a single FeatureGroup.

                  get

                  GET /v1/{name}

                  Gets details of a single FeatureGroup.

                  getIamPolicy

                  POST /v1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1/{parent}/featureGroups

                  Lists FeatureGroups in a given project and location.

                  patch

                  PATCH /v1/{featureGroup.name}

                  Updates the parameters of a single FeatureGroup.

                  setIamPolicy

                  POST /v1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  testIamPermissions

                  POST /v1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1.projects.locations.featureGroups.features

                Methods

                  batchCreate

                  POST /v1/{parent}/features:batchCreate

                  Creates a batch of Features in a given FeatureGroup.

                  create

                  POST /v1/{parent}/features

                  Creates a new Feature in a given FeatureGroup.

                  delete

                  DELETE /v1/{name}

                  Deletes a single Feature.

                  get

                  GET /v1/{name}

                  Gets details of a single Feature.

                  list

                  GET /v1/{parent}/features

                  Lists Features in a given FeatureGroup.

                  patch

                  PATCH /v1/{feature.name}

                  Updates the parameters of a single Feature.

        REST Resource: v1.projects.locations.featureOnlineStores

                Methods

                  create

                  POST /v1/{parent}/featureOnlineStores

                  Creates a new FeatureOnlineStore in a given project and location.

                  delete

                  DELETE /v1/{name}

                  Deletes a single FeatureOnlineStore.

                  get

                  GET /v1/{name}

                  Gets details of a single FeatureOnlineStore.

                  getIamPolicy

                  POST /v1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1/{parent}/featureOnlineStores

                  Lists FeatureOnlineStores in a given project and location.

                  patch

                  PATCH /v1/{featureOnlineStore.name}

                  Updates the parameters of a single FeatureOnlineStore.

                  setIamPolicy

                  POST /v1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  testIamPermissions

                  POST /v1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1.projects.locations.featureOnlineStores.featureViews

                Methods

                  create

                  POST /v1/{parent}/featureViews

                  Creates a new FeatureView in a given FeatureOnlineStore.

                  delete

                  DELETE /v1/{name}

                  Deletes a single FeatureView.

                  directWrite

                  POST /v1/{featureView}:directWrite

                  Bidirectional streaming RPC to directly write to feature values in a feature view.

                  fetchFeatureValues

                  POST /v1/{featureView}:fetchFeatureValues

                  Fetch feature values under a FeatureView.

                  generateFetchAccessToken

                  POST /v1/{featureView}:generateFetchAccessToken

                  RPC to generate an access token for the given feature view.

                  get

                  GET /v1/{name}

                  Gets details of a single FeatureView.

                  getIamPolicy

                  POST /v1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1/{parent}/featureViews

                  Lists FeatureViews in a given FeatureOnlineStore.

                  patch

                  PATCH /v1/{featureView.name}

                  Updates the parameters of a single FeatureView.

                  searchNearestEntities

                  POST /v1/{featureView}:searchNearestEntities

                  Search the nearest entities under a FeatureView.

                  setIamPolicy

                  POST /v1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  sync

                  POST /v1/{featureView}:sync

                  Triggers on-demand sync for the FeatureView.

                  testIamPermissions

                  POST /v1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1.projects.locations.featureOnlineStores.featureViews.featureViewSyncs

                Methods

                  get

                  GET /v1/{name}

                  Gets details of a single FeatureViewSync.

                  list

                  GET /v1/{parent}/featureViewSyncs

                  Lists FeatureViewSyncs in a given FeatureView.

        REST Resource: v1.projects.locations.featurestores

                Methods

                  batchReadFeatureValues

                  POST /v1/{featurestore}:batchReadFeatureValues

                  Batch reads Feature values from a Featurestore.

                  create

                  POST /v1/{parent}/featurestores

                  Creates a new Featurestore in a given project and location.

                  delete

                  DELETE /v1/{name}

                  Deletes a single Featurestore.

                  get

                  GET /v1/{name}

                  Gets details of a single Featurestore.

                  getIamPolicy

                  POST /v1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1/{parent}/featurestores

                  Lists Featurestores in a given project and location.

                  patch

                  PATCH /v1/{featurestore.name}

                  Updates the parameters of a single Featurestore.

                  searchFeatures

                  GET /v1/{location}/featurestores:searchFeatures

                  Searches Features matching a query in a given project.

                  setIamPolicy

                  POST /v1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  testIamPermissions

                  POST /v1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1.projects.locations.featurestores.entityTypes

                Methods

                  create

                  POST /v1/{parent}/entityTypes

                  Creates a new EntityType in a given Featurestore.

                  delete

                  DELETE /v1/{name}

                  Deletes a single EntityType.

                  deleteFeatureValues

                  POST /v1/{entityType}:deleteFeatureValues

                  Delete Feature values from Featurestore.

                  exportFeatureValues

                  POST /v1/{entityType}:exportFeatureValues

                  Exports Feature values from all the entities of a target EntityType.

                  get

                  GET /v1/{name}

                  Gets details of a single EntityType.

                  getIamPolicy

                  POST /v1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  importFeatureValues

                  POST /v1/{entityType}:importFeatureValues

                  Imports Feature values into the Featurestore from a source storage.

                  list

                  GET /v1/{parent}/entityTypes

                  Lists EntityTypes in a given Featurestore.

                  patch

                  PATCH /v1/{entityType.name}

                  Updates the parameters of a single EntityType.

                  readFeatureValues

                  POST /v1/{entityType}:readFeatureValues

                  Reads Feature values of a specific entity of an EntityType.

                  setIamPolicy

                  POST /v1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  streamingReadFeatureValues

                  POST /v1/{entityType}:streamingReadFeatureValues

                  Reads Feature values for multiple entities.

                  testIamPermissions

                  POST /v1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

                  writeFeatureValues

                  POST /v1/{entityType}:writeFeatureValues

                  Writes Feature values of one or more entities of an EntityType.

        REST Resource: v1.projects.locations.featurestores.entityTypes.features

                Methods

                  batchCreate

                  POST /v1/{parent}/features:batchCreate

                  Creates a batch of Features in a given EntityType.

                  create

                  POST /v1/{parent}/features

                  Creates a new Feature in a given EntityType.

                  delete

                  DELETE /v1/{name}

                  Deletes a single Feature.

                  get

                  GET /v1/{name}

                  Gets details of a single Feature.

                  list

                  GET /v1/{parent}/features

                  Lists Features in a given EntityType.

                  patch

                  PATCH /v1/{feature.name}

                  Updates the parameters of a single Feature.

        REST Resource: v1.projects.locations.hyperparameterTuningJobs

                Methods

                  cancel

                  POST /v1/{name}:cancel

                  Cancels a HyperparameterTuningJob.

                  create

                  POST /v1/{parent}/hyperparameterTuningJobs

                  Creates a HyperparameterTuningJob

                  delete

                  DELETE /v1/{name}

                  Deletes a HyperparameterTuningJob.

                  get

                  GET /v1/{name}

                  Gets a HyperparameterTuningJob

                  list

                  GET /v1/{parent}/hyperparameterTuningJobs

                  Lists HyperparameterTuningJobs in a Location.

        REST Resource: v1.projects.locations.indexEndpoints

                Methods

                  create

                  POST /v1/{parent}/indexEndpoints

                  Creates an IndexEndpoint.

                  delete

                  DELETE /v1/{name}

                  Deletes an IndexEndpoint.

                  deployIndex

                  POST /v1/{indexEndpoint}:deployIndex

                  Deploys an Index into this IndexEndpoint, creating a DeployedIndex within it.

                  get

                  GET /v1/{name}

                  Gets an IndexEndpoint.

                  list

                  GET /v1/{parent}/indexEndpoints

                  Lists IndexEndpoints in a Location.

                  mutateDeployedIndex

                  POST /v1/{indexEndpoint}:mutateDeployedIndex

                  Update an existing DeployedIndex under an IndexEndpoint.

                  patch

                  PATCH /v1/{indexEndpoint.name}

                  Updates an IndexEndpoint.

                  undeployIndex

                  POST /v1/{indexEndpoint}:undeployIndex

                  Undeploys an Index from an IndexEndpoint, removing a DeployedIndex from it, and freeing all resources it's using.

        REST Resource: v1.projects.locations.indexes

                Methods

                  create

                  POST /v1/{parent}/indexes

                  Creates an Index.

                  delete

                  DELETE /v1/{name}

                  Deletes an Index.

                  get

                  GET /v1/{name}

                  Gets an Index.

                  list

                  GET /v1/{parent}/indexes

                  Lists Indexes in a Location.

                  patch

                  PATCH /v1/{index.name}

                  Updates an Index.

                  removeDatapoints

                  POST /v1/{index}:removeDatapoints

                  Remove Datapoints from an Index.

                  upsertDatapoints

                  POST /v1/{index}:upsertDatapoints

                  Add/update Datapoints into an Index.

        REST Resource: v1.projects.locations.metadataStores

                Methods

                  create

                  POST /v1/{parent}/metadataStores

                  Initializes a MetadataStore, including allocation of resources.

                  delete

                  DELETE /v1/{name}

                  Deletes a single MetadataStore and all its child resources (Artifacts, Executions, and Contexts).

                  get

                  GET /v1/{name}

                  Retrieves a specific MetadataStore.

                  list

                  GET /v1/{parent}/metadataStores

                  Lists MetadataStores for a Location.

        REST Resource: v1.projects.locations.metadataStores.artifacts

                Methods

                  create

                  POST /v1/{parent}/artifacts

                  Creates an Artifact associated with a MetadataStore.

                  delete

                  DELETE /v1/{name}

                  Deletes an Artifact.

                  get

                  GET /v1/{name}

                  Retrieves a specific Artifact.

                  list

                  GET /v1/{parent}/artifacts

                  Lists Artifacts in the MetadataStore.

                  patch

                  PATCH /v1/{artifact.name}

                  Updates a stored Artifact.

                  purge

                  POST /v1/{parent}/artifacts:purge

                  Purges Artifacts.

                  queryArtifactLineageSubgraph

                  GET /v1/{artifact}:queryArtifactLineageSubgraph

                  Retrieves lineage of an Artifact represented through Artifacts and Executions connected by Event edges and returned as a LineageSubgraph.

        REST Resource: v1.projects.locations.metadataStores.contexts

                Methods

                  addContextArtifactsAndExecutions

                  POST /v1/{context}:addContextArtifactsAndExecutions

                  Adds a set of Artifacts and Executions to a Context.

                  addContextChildren

                  POST /v1/{context}:addContextChildren

                  Adds a set of Contexts as children to a parent Context.

                  create

                  POST /v1/{parent}/contexts

                  Creates a Context associated with a MetadataStore.

                  delete

                  DELETE /v1/{name}

                  Deletes a stored Context.

                  get

                  GET /v1/{name}

                  Retrieves a specific Context.

                  list

                  GET /v1/{parent}/contexts

                  Lists Contexts on the MetadataStore.

                  patch

                  PATCH /v1/{context.name}

                  Updates a stored Context.

                  purge

                  POST /v1/{parent}/contexts:purge

                  Purges Contexts.

                  queryContextLineageSubgraph

                  GET /v1/{context}:queryContextLineageSubgraph

                  Retrieves Artifacts and Executions within the specified Context, connected by Event edges and returned as a LineageSubgraph.

                  removeContextChildren

                  POST /v1/{context}:removeContextChildren

                  Remove a set of children contexts from a parent Context.

        REST Resource: v1.projects.locations.metadataStores.executions

                Methods

                  addExecutionEvents

                  POST /v1/{execution}:addExecutionEvents

                  Adds Events to the specified Execution.

                  create

                  POST /v1/{parent}/executions

                  Creates an Execution associated with a MetadataStore.

                  delete

                  DELETE /v1/{name}

                  Deletes an Execution.

                  get

                  GET /v1/{name}

                  Retrieves a specific Execution.

                  list

                  GET /v1/{parent}/executions

                  Lists Executions in the MetadataStore.

                  patch

                  PATCH /v1/{execution.name}

                  Updates a stored Execution.

                  purge

                  POST /v1/{parent}/executions:purge

                  Purges Executions.

                  queryExecutionInputsAndOutputs

                  GET /v1/{execution}:queryExecutionInputsAndOutputs

                  Obtains the set of input and output Artifacts for this Execution, in the form of LineageSubgraph that also contains the Execution and connecting Events.

        REST Resource: v1.projects.locations.metadataStores.metadataSchemas

                Methods

                  create

                  POST /v1/{parent}/metadataSchemas

                  Creates a MetadataSchema.

                  get

                  GET /v1/{name}

                  Retrieves a specific MetadataSchema.

                  list

                  GET /v1/{parent}/metadataSchemas

                  Lists MetadataSchemas.

        REST Resource: v1.projects.locations.migratableResources

                Methods

                  batchMigrate

                  POST /v1/{parent}/migratableResources:batchMigrate

                  Batch migrates resources from ml.googleapis.com, automl.googleapis.com, and datalabeling.googleapis.com to Agent Platform.

                  search

                  POST /v1/{parent}/migratableResources:search

                  Searches all of the resources in automl.googleapis.com, datalabeling.googleapis.com and ml.googleapis.com that can be migrated to Agent Platform's given location.

        REST Resource: v1.projects.locations.modelDeploymentMonitoringJobs

                Methods

                  create

                  POST /v1/{parent}/modelDeploymentMonitoringJobs

                  Creates a ModelDeploymentMonitoringJob.

                  delete

                  DELETE /v1/{name}

                  Deletes a ModelDeploymentMonitoringJob.

                  get

                  GET /v1/{name}

                  Gets a ModelDeploymentMonitoringJob.

                  list

                  GET /v1/{parent}/modelDeploymentMonitoringJobs

                  Lists ModelDeploymentMonitoringJobs in a Location.

                  patch

                  PATCH /v1/{modelDeploymentMonitoringJob.name}

                  Updates a ModelDeploymentMonitoringJob.

                  pause

                  POST /v1/{name}:pause

                  Pauses a ModelDeploymentMonitoringJob.

                  resume

                  POST /v1/{name}:resume

                  Resumes a paused ModelDeploymentMonitoringJob.

                  searchModelDeploymentMonitoringStatsAnomalies

                  POST /v1/{modelDeploymentMonitoringJob}:searchModelDeploymentMonitoringStatsAnomalies

                  Searches Model Monitoring Statistics generated within a given time window.

        REST Resource: v1.projects.locations.models

                Methods

                  copy

                  POST /v1/{parent}/models:copy

                  Copies an already existing Agent Platform Model into the specified Location.

                  delete

                  DELETE /v1/{name}

                  Deletes a Model.

                  deleteVersion

                  DELETE /v1/{name}:deleteVersion

                  Deletes a Model version.

                  export

                  POST /v1/{name}:export

                  Exports a trained, exportable Model to a location specified by the user.

                  get

                  GET /v1/{name}

                  Gets a Model.

                  getIamPolicy

                  POST /v1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1/{parent}/models

                  Lists Models in a Location.

                  listCheckpoints

                  GET /v1/{name}:listCheckpoints

                  Lists checkpoints of the specified model version.

                  listVersions

                  GET /v1/{name}:listVersions

                  Lists versions of the specified model.

                  mergeVersionAliases

                  POST /v1/{name}:mergeVersionAliases

                  Merges a set of aliases for a Model version.

                  patch

                  PATCH /v1/{model.name}

                  Updates a Model.

                  setIamPolicy

                  POST /v1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  testIamPermissions

                  POST /v1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

                  updateExplanationDataset

                  POST /v1/{model}:updateExplanationDataset

                  Incrementally update the dataset used for an examples model.

                  upload

                  POST /v1/{parent}/models:upload

                  Uploads a Model artifact into Agent Platform.

        REST Resource: v1.projects.locations.models.evaluations

                Methods

                  get

                  GET /v1/{name}

                  Gets a ModelEvaluation.

                  import

                  POST /v1/{parent}/evaluations:import

                  Imports an externally generated ModelEvaluation.

                  list

                  GET /v1/{parent}/evaluations

                  Lists ModelEvaluations in a Model.

        REST Resource: v1.projects.locations.models.evaluations.slices

                Methods

                  batchImport

                  POST /v1/{parent}:batchImport

                  Imports a list of externally generated EvaluatedAnnotations.

                  get

                  GET /v1/{name}

                  Gets a ModelEvaluationSlice.

                  list

                  GET /v1/{parent}/slices

                  Lists ModelEvaluationSlices in a ModelEvaluation.

        REST Resource: v1.projects.locations.nasJobs

                Methods

                  cancel

                  POST /v1/{name}:cancel

                  Cancels a NasJob.

                  create

                  POST /v1/{parent}/nasJobs

                  Creates a NasJob

                  delete

                  DELETE /v1/{name}

                  Deletes a NasJob.

                  get

                  GET /v1/{name}

                  Gets a NasJob

                  list

                  GET /v1/{parent}/nasJobs

                  Lists NasJobs in a Location.

        REST Resource: v1.projects.locations.nasJobs.nasTrialDetails

                Methods

                  get

                  GET /v1/{name}

                  Gets a NasTrialDetail.

                  list

                  GET /v1/{parent}/nasTrialDetails

                  List top NasTrialDetails of a NasJob.

        REST Resource: v1.projects.locations.notebookExecutionJobs

                Methods

                  create

                  POST /v1/{parent}/notebookExecutionJobs

                  Creates a NotebookExecutionJob.

                  delete

                  DELETE /v1/{name}

                  Deletes a NotebookExecutionJob.

                  get

                  GET /v1/{name}

                  Gets a NotebookExecutionJob.

                  list

                  GET /v1/{parent}/notebookExecutionJobs

                  Lists NotebookExecutionJobs in a Location.

        REST Resource: v1.projects.locations.notebookRuntimeTemplates

                Methods

                  create

                  POST /v1/{parent}/notebookRuntimeTemplates

                  Creates a NotebookRuntimeTemplate.

                  delete

                  DELETE /v1/{name}

                  Deletes a NotebookRuntimeTemplate.

                  get

                  GET /v1/{name}

                  Gets a NotebookRuntimeTemplate.

                  getIamPolicy

                  POST /v1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1/{parent}/notebookRuntimeTemplates

                  Lists NotebookRuntimeTemplates in a Location.

                  patch

                  PATCH /v1/{notebookRuntimeTemplate.name}

                  Updates a NotebookRuntimeTemplate.

                  setIamPolicy

                  POST /v1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  testIamPermissions

                  POST /v1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1.projects.locations.notebookRuntimes

                Methods

                  assign

                  POST /v1/{parent}/notebookRuntimes:assign

                  Assigns a NotebookRuntime to a user for a particular Notebook file.

                  delete

                  DELETE /v1/{name}

                  Deletes a NotebookRuntime.

                  get

                  GET /v1/{name}

                  Gets a NotebookRuntime.

                  list

                  GET /v1/{parent}/notebookRuntimes

                  Lists NotebookRuntimes in a Location.

                  start

                  POST /v1/{name}:start

                  Starts a NotebookRuntime.

                  stop

                  POST /v1/{name}:stop

                  Stops a NotebookRuntime.

                  upgrade

                  POST /v1/{name}:upgrade

                  Upgrades a NotebookRuntime.

        REST Resource: v1.projects.locations.operations

                Methods

                  cancel

                  POST /v1/{name}:cancel

                  Starts asynchronous cancellation on a long-running operation.

                  delete

                  DELETE /v1/{name}

                  Deletes a long-running operation.

                  get

                  GET /v1/{name}

                  Gets the latest state of a long-running operation.

                  list

                  GET /v1/{name}/operations

                  Lists operations that match the specified filter in the request.

                  wait

                  POST /v1/{name}:wait

                  Waits until the specified long-running operation is done or reaches at most a specified timeout, returning the latest state.

        REST Resource: v1.projects.locations.persistentResources

                Methods

                  create

                  POST /v1/{parent}/persistentResources

                  Creates a PersistentResource.

                  delete

                  DELETE /v1/{name}

                  Deletes a PersistentResource.

                  get

                  GET /v1/{name}

                  Gets a PersistentResource.

                  list

                  GET /v1/{parent}/persistentResources

                  Lists PersistentResources in a Location.

                  patch

                  PATCH /v1/{persistentResource.name}

                  Updates a PersistentResource.

                  reboot

                  POST /v1/{name}:reboot

                  Reboots a PersistentResource.

        REST Resource: v1.projects.locations.pipelineJobs

                Methods

                  batchCancel

                  POST /v1/{parent}/pipelineJobs:batchCancel

                  Batch cancel PipelineJobs.

                  batchDelete

                  POST /v1/{parent}/pipelineJobs:batchDelete

                  Batch deletes PipelineJobs The Operation is atomic.

                  cancel

                  POST /v1/{name}:cancel

                  Cancels a PipelineJob.

                  create

                  POST /v1/{parent}/pipelineJobs

                  Creates a PipelineJob.

                  delete

                  DELETE /v1/{name}

                  Deletes a PipelineJob.

                  get

                  GET /v1/{name}

                  Gets a PipelineJob.

                  list

                  GET /v1/{parent}/pipelineJobs

                  Lists PipelineJobs in a Location.

        REST Resource: v1.projects.locations.publishers.models

                Methods

                  computeTokens

                  POST /v1/{endpoint}:computeTokens

                  Return a list of tokens based on the input text.

                  countTokens

                  POST /v1/{endpoint}:countTokens

                  Perform a token counting.

                  embedContent

                  POST /v1/{model}:embedContent

                  Embed content with multimodal inputs.

                  generateContent

                  POST /v1/{model}:generateContent

                  Generate content with multimodal inputs.

                  predict

                  POST /v1/{endpoint}:predict

                  Perform an online inference.

                  rawPredict

                  POST /v1/{endpoint}:rawPredict

                  Perform an online prediction with an arbitrary HTTP payload.

                  serverStreamingPredict

                  POST /v1/{endpoint}:serverStreamingPredict

                  Perform a server-side streaming online prediction request for Vertex LLM streaming.

                  streamGenerateContent

                  POST /v1/{model}:streamGenerateContent

                  Generate content with multimodal inputs with streaming support.

                  streamRawPredict

                  POST /v1/{endpoint}:streamRawPredict

                  Perform a streaming online prediction with an arbitrary HTTP payload.

        REST Resource: v1.projects.locations.publishers.v1.responses

                Methods

                  delete

                  DELETE /v1/{name}

                  Deletes the response from the endpoint.

                  get

                  GET /v1/{name}

                  Gets the response from the endpoint.

        REST Resource: v1.projects.locations.ragCorpora

                Methods

                  create

                  POST /v1/{parent}/ragCorpora

                  Creates a RagCorpus.

                  delete

                  DELETE /v1/{name}

                  Deletes a RagCorpus.

                  get

                  GET /v1/{name}

                  Gets a RagCorpus.

                  list

                  GET /v1/{parent}/ragCorpora

                  Lists RagCorpora in a Location.

                  patch

                  PATCH /v1/{ragCorpus.name}

                  Updates a RagCorpus.

        REST Resource: v1.projects.locations.ragCorpora.ragFiles

                Methods

                  delete

                  DELETE /v1/{name}

                  Deletes a RagFile.

                  get

                  GET /v1/{name}

                  Gets a RagFile.

                  import

                  POST /v1/{parent}/ragFiles:import

                  Import files from Google Cloud Storage or Google Drive into a RagCorpus.

                  list

                  GET /v1/{parent}/ragFiles

                  Lists RagFiles in a RagCorpus.

        REST Resource: v1.projects.locations.reasoningEngines

                Methods

                  asyncQuery

                  POST /v1/{name}:asyncQuery

                  Async query using a reasoning engine.

                  cancelAsyncQuery

                  POST /v1/{name}:cancelAsyncQuery

                  Cancels an AsyncQueryReasoningEngine operation.

                  create

                  POST /v1/{parent}/reasoningEngines

                  Creates a reasoning engine.

                  delete

                  DELETE /v1/{name}

                  Deletes a reasoning engine.

                  executeCode

                  POST /v1/{name}:executeCode

                  Executes code statelessly.

                  get

                  GET /v1/{name}

                  Gets a reasoning engine.

                  getIamPolicy

                  POST /v1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1/{parent}/reasoningEngines

                  Lists reasoning engines in a location.

                  patch

                  PATCH /v1/{reasoningEngine.name}

                  Updates a reasoning engine.

                  query

                  POST /v1/{name}:query

                  Queries using a reasoning engine.

                  setIamPolicy

                  POST /v1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  streamQuery

                  POST /v1/{name}:streamQuery

                  Streams queries using a reasoning engine.

                  testIamPermissions

                  POST /v1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1.projects.locations.reasoningEngines.runtimeRevisions

                Methods

                  query

                  POST /v1/{name}:query

                  Queries using a reasoning engine.

                  streamQuery

                  POST /v1/{name}:streamQuery

                  Streams queries using a reasoning engine.

        REST Resource: v1.projects.locations.reasoningEngines.sandboxEnvironmentSnapshots

                Methods

                  delete

                  DELETE /v1/{name}

                  Deletes the specific SandboxEnvironmentSnapshot.

                  get

                  GET /v1/{name}

                  Gets details of the specific SandboxEnvironmentSnapshot.

                  list

                  GET /v1/{parent}/sandboxEnvironmentSnapshots

                  Lists SandboxEnvironmentSnapshots in a given reasoning engine.

        REST Resource: v1.projects.locations.reasoningEngines.sandboxEnvironmentTemplates

                Methods

                  create

                  POST /v1/{parent}/sandboxEnvironmentTemplates

                  Creates a SandboxEnvironmentTemplate in a given reasoning engine.

                  delete

                  DELETE /v1/{name}

                  Deletes the specific SandboxEnvironmentTemplate.

                  get

                  GET /v1/{name}

                  Gets details of the specific SandboxEnvironmentTemplate.

                  list

                  GET /v1/{parent}/sandboxEnvironmentTemplates

                  Lists SandboxEnvironmentTemplates in a given reasoning engine.

        REST Resource: v1.projects.locations.reasoningEngines.sandboxEnvironments

                Methods

                  authorizeAccess

                  POST /v1/{name}:authorizeAccess

                  Checks whether the caller is authorized to access the sandbox environment.

                  create

                  POST /v1/{parent}/sandboxEnvironments

                  Creates a SandboxEnvironment in a given reasoning engine.

                  delete

                  DELETE /v1/{name}

                  Deletes the specific SandboxEnvironment.

                  execute

                  POST /v1/{name}:execute

                  Executes using a sandbox environment.

                  get

                  GET /v1/{name}

                  Gets details of the specific SandboxEnvironment.

                  list

                  GET /v1/{parent}/sandboxEnvironments

                  Lists SandboxEnvironments in a given reasoning engine.

                  pause

                  POST /v1/{name}:pause

                  Pauses the specific SandboxEnvironment.

                  resume

                  POST /v1/{name}:resume

                  Resumes the specific SandboxEnvironment.

                  snapshot

                  POST /v1/{name}:snapshot

                  Snapshots the specific SandboxEnvironment resource and creates a SandboxEnvironmentSnapshot resource.

        REST Resource: v1.projects.locations.reasoningEngines.sessions

                Methods

                  appendEvent

                  POST /v1/{name}:appendEvent

                  Appends an event to a given session.

                  create

                  POST /v1/{parent}/sessions

                  Creates a new Session.

                  delete

                  DELETE /v1/{name}

                  Deletes details of the specific Session.

                  get

                  GET /v1/{name}

                  Gets details of the specific Session.

                  list

                  GET /v1/{parent}/sessions

                  Lists Sessions in a given reasoning engine.

                  patch

                  PATCH /v1/{session.name}

                  Updates the specific Session.

        REST Resource: v1.projects.locations.reasoningEngines.sessions.events

                Methods

                  list

                  GET /v1/{parent}/events

                  Lists Events in a given session.

        REST Resource: v1.projects.locations.schedules

                Methods

                  create

                  POST /v1/{parent}/schedules

                  Creates a Schedule.

                  delete

                  DELETE /v1/{name}

                  Deletes a Schedule.

                  get

                  GET /v1/{name}

                  Gets a Schedule.

                  list

                  GET /v1/{parent}/schedules

                  Lists Schedules in a Location.

                  patch

                  PATCH /v1/{schedule.name}

                  Updates an active or paused Schedule.

                  pause

                  POST /v1/{name}:pause

                  Pauses a Schedule.

                  resume

                  POST /v1/{name}:resume

                  Resumes a paused Schedule to start scheduling new runs.

        REST Resource: v1.projects.locations.semanticGovernancePolicies

                Methods

                  create

                  POST /v1/{parent}/semanticGovernancePolicies

                  Creates a SemanticGovernancePolicy.

                  delete

                  DELETE /v1/{name}

                  Deletes a SemanticGovernancePolicy.

                  get

                  GET /v1/{name}

                  Gets a SemanticGovernancePolicy.

                  list

                  GET /v1/{parent}/semanticGovernancePolicies

                  Lists SemanticGovernancePolicies in a given location.

                  patch

                  PATCH /v1/{semanticGovernancePolicy.name}

                  Updates a SemanticGovernancePolicy.

        REST Resource: v1.projects.locations.semanticGovernancePolicyEngine

                Methods

                  deprovision

                  POST /v1/{name}:deprovision

                  Deprovisions the SemanticGovernancePolicyEngine, tearing down the associated tenant project, GKE cluster, and PSC service attachments.

        REST Resource: v1.projects.locations.specialistPools

                Methods

                  create

                  POST /v1/{parent}/specialistPools

                  Creates a SpecialistPool.

                  delete

                  DELETE /v1/{name}

                  Deletes a SpecialistPool as well as all Specialists in the pool.

                  get

                  GET /v1/{name}

                  Gets a SpecialistPool.

                  list

                  GET /v1/{parent}/specialistPools

                  Lists SpecialistPools in a Location.

                  patch

                  PATCH /v1/{specialistPool.name}

                  Updates a SpecialistPool.

        REST Resource: v1.projects.locations.studies

                Methods

                  create

                  POST /v1/{parent}/studies

                  Creates a Study.

                  delete

                  DELETE /v1/{name}

                  Deletes a Study.

                  get

                  GET /v1/{name}

                  Gets a Study by name.

                  list

                  GET /v1/{parent}/studies

                  Lists all the studies in a region for an associated project.

                  lookup

                  POST /v1/{parent}/studies:lookup

                  Looks a study up using the user-defined display_name field instead of the fully qualified resource name.

        REST Resource: v1.projects.locations.studies.trials

                Methods

                  addTrialMeasurement

                  POST /v1/{trialName}:addTrialMeasurement

                  Adds a measurement of the objective metrics to a Trial.

                  checkTrialEarlyStoppingState

                  POST /v1/{trialName}:checkTrialEarlyStoppingState

                  Checks whether a Trial should stop or not.

                  complete

                  POST /v1/{name}:complete

                  Marks a Trial as complete.

                  create

                  POST /v1/{parent}/trials

                  Adds a user provided Trial to a Study.

                  delete

                  DELETE /v1/{name}

                  Deletes a Trial.

                  get

                  GET /v1/{name}

                  Gets a Trial.

                  list

                  GET /v1/{parent}/trials

                  Lists the Trials associated with a Study.

                  listOptimalTrials

                  POST /v1/{parent}/trials:listOptimalTrials

                  Lists the pareto-optimal Trials for multi-objective Study or the optimal Trials for single-objective Study.

                  stop

                  POST /v1/{name}:stop

                  Stops a Trial.

                  suggest

                  POST /v1/{parent}/trials:suggest

                  Adds one or more Trials to a Study, with parameter values suggested by Agent Platform Vizier.

        REST Resource: v1.projects.locations.tensorboards

                Methods

                  batchRead

                  GET /v1/{tensorboard}:batchRead

                  Reads multiple TensorboardTimeSeries' data.

                  create

                  POST /v1/{parent}/tensorboards

                  Creates a Tensorboard.

                  delete

                  DELETE /v1/{name}

                  Deletes a Tensorboard.

                  get

                  GET /v1/{name}

                  Gets a Tensorboard.

                  list

                  GET /v1/{parent}/tensorboards

                  Lists Tensorboards in a Location.

                  patch

                  PATCH /v1/{tensorboard.name}

                  Updates a Tensorboard.

                  readSize

                  GET /v1/{tensorboard}:readSize

                  Returns the storage size for a given TensorBoard instance.

                  readUsage

                  GET /v1/{tensorboard}:readUsage

                  Returns a list of monthly active users for a given TensorBoard instance.

        REST Resource: v1.projects.locations.tensorboards.experiments

                Methods

                  batchCreate

                  POST /v1/{parent}:batchCreate

                  Batch create TensorboardTimeSeries that belong to a TensorboardExperiment.

                  create

                  POST /v1/{parent}/experiments

                  Creates a TensorboardExperiment.

                  delete

                  DELETE /v1/{name}

                  Deletes a TensorboardExperiment.

                  get

                  GET /v1/{name}

                  Gets a TensorboardExperiment.

                  list

                  GET /v1/{parent}/experiments

                  Lists TensorboardExperiments in a Location.

                  patch

                  PATCH /v1/{tensorboardExperiment.name}

                  Updates a TensorboardExperiment.

                  write

                  POST /v1/{tensorboardExperiment}:write

                  Write time series data points of multiple TensorboardTimeSeries in multiple TensorboardRun's.

        REST Resource: v1.projects.locations.tensorboards.experiments.runs

                Methods

                  batchCreate

                  POST /v1/{parent}/runs:batchCreate

                  Batch create TensorboardRuns.

                  create

                  POST /v1/{parent}/runs

                  Creates a TensorboardRun.

                  delete

                  DELETE /v1/{name}

                  Deletes a TensorboardRun.

                  get

                  GET /v1/{name}

                  Gets a TensorboardRun.

                  list

                  GET /v1/{parent}/runs

                  Lists TensorboardRuns in a Location.

                  patch

                  PATCH /v1/{tensorboardRun.name}

                  Updates a TensorboardRun.

                  write

                  POST /v1/{tensorboardRun}:write

                  Write time series data points into multiple TensorboardTimeSeries under a TensorboardRun.

        REST Resource: v1.projects.locations.tensorboards.experiments.runs.timeSeries

                Methods

                  create

                  POST /v1/{parent}/timeSeries

                  Creates a TensorboardTimeSeries.

                  delete

                  DELETE /v1/{name}

                  Deletes a TensorboardTimeSeries.

                  exportTensorboardTimeSeries

                  POST /v1/{tensorboardTimeSeries}:exportTensorboardTimeSeries

                  Exports a TensorboardTimeSeries' data.

                  get

                  GET /v1/{name}

                  Gets a TensorboardTimeSeries.

                  list

                  GET /v1/{parent}/timeSeries

                  Lists TensorboardTimeSeries in a Location.

                  patch

                  PATCH /v1/{tensorboardTimeSeries.name}

                  Updates a TensorboardTimeSeries.

                  read

                  GET /v1/{tensorboardTimeSeries}:read

                  Reads a TensorboardTimeSeries' data.

                  readBlobData

                  GET /v1/{timeSeries}:readBlobData

                  Gets bytes of TensorboardBlobs.

        REST Resource: v1.projects.locations.trainingPipelines

                Methods

                  cancel

                  POST /v1/{name}:cancel

                  Cancels a TrainingPipeline.

                  create

                  POST /v1/{parent}/trainingPipelines

                  Creates a TrainingPipeline.

                  delete

                  DELETE /v1/{name}

                  Deletes a TrainingPipeline.

                  get

                  GET /v1/{name}

                  Gets a TrainingPipeline.

                  list

                  GET /v1/{parent}/trainingPipelines

                  Lists TrainingPipelines in a Location.

        REST Resource: v1.projects.locations.tuningJobs

                Methods

                  cancel

                  POST /v1/{name}:cancel

                  Cancels a tuning job.

                  create

                  POST /v1/{parent}/tuningJobs

                  Creates a tuning job.

                  get

                  GET /v1/{name}

                  Gets a tuning job.

                  list

                  GET /v1/{parent}/tuningJobs

                  Lists tuning jobs in a location.

                  rebaseTunedModel

                  POST /v1/{parent}/tuningJobs:rebaseTunedModel

                  Rebase a tuned model.

        REST Resource: v1.publishers.models

                Methods

                  get

                  GET /v1/{name}

                  Gets a Model Garden publisher model.

        REST Resource: v1beta1.interactions

                Methods

                  cancel

                  POST /v1beta1/{name}:cancel

                  Cancels an interaction.

                  getPoll

                  GET /v1beta1/{name}:poll

                  Fully typed proto, unary version of GetInteraction that returns Interaction proto.

                  getStream

                  GET /v1beta1/{name}:stream

                  Fully typed proto, streaming version of GetInteraction that returns Interaction proto.

        REST Resource: v1beta1.media

                Methods

                  upload

                  POST /v1beta1/{parent}/ragFiles:upload

                  POST /upload/v1beta1/{parent}/ragFiles:upload

                  Upload a file into a RagCorpus.

        REST Resource: v1beta1.operations

                Methods

                  cancel

                  POST /v1beta1/{name}:cancel

                  Starts asynchronous cancellation on a long-running operation.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a long-running operation.

                  get

                  GET /v1beta1/{name}

                  Gets the latest state of a long-running operation.

                  list

                  GET /v1beta1/operations

                  Lists operations that match the specified filter in the request.

                  wait

                  POST /v1beta1/{name}:wait

                  Waits until the specified long-running operation is done or reaches at most a specified timeout, returning the latest state.

        REST Resource: v1beta1.projects

                Methods

                  fetchPublisherModelConfig

                  GET /v1beta1/{name}:fetchPublisherModelConfig

                  Fetches the configs of publisher models.

                  setPublisherModelConfig

                  POST /v1beta1/{name}:setPublisherModelConfig

                  Sets (creates or updates) configs of publisher models.

        REST Resource: v1beta1.projects.locations

                Methods

                  askContexts

                  POST /v1beta1/{parent}:askContexts

                  Agentic Retrieval Ask API for RAG.

                  asyncRetrieveContexts

                  POST /v1beta1/{parent}:asyncRetrieveContexts

                  Asynchronous API to retrieves relevant contexts for a query.

                  augmentPrompt

                  POST /v1beta1/{parent}:augmentPrompt

                  Given an input prompt, it returns augmented prompt from vertex rag store  to guide LLM towards generating grounded responses.

                  corroborateContent

                  POST /v1beta1/{parent}:corroborateContent

                  Given an input text, it returns a score that evaluates the factuality of the text.

                  deploy

                  POST /v1beta1/{destination}:deploy

                  Deploys a model to a new endpoint.

                  deployPublisherModel
(deprecated)

                  POST /v1beta1/{destination}:deployPublisherModel

                  Deploys publisher models.

                  evaluateDataset

                  POST /v1beta1/{location}:evaluateDataset

                  Evaluates a dataset based on a set of given metrics.

                  evaluateInstances

                  POST /v1beta1/{location}:evaluateInstances

                  Evaluates instances based on a given metric.

                  generateInstanceRubrics

                  POST /v1beta1/{location}:generateInstanceRubrics

                  Generates rubrics for a given prompt.

                  generateLossClusters

                  POST /v1beta1/{location}:generateLossClusters

                  Generates loss clusters from evaluation results.

                  generateSyntheticData

                  POST /v1beta1/{location}:generateSyntheticData

                  Generates synthetic (artificial) data based on a description

                  getRagEngineConfig

                  GET /v1beta1/{name}

                  Gets a RagEngineConfig.

                  getSemanticGovernancePolicyEngine

                  GET /v1beta1/{name}

                  Gets a SemanticGovernancePolicyEngine.

                  recommendSpec

                  POST /v1beta1/{parent}:recommendSpec

                  Gets a Model's spec recommendations.

                  retrieveContexts

                  POST /v1beta1/{parent}:retrieveContexts

                  Retrieves relevant contexts for a query.

                  updateRagEngineConfig

                  PATCH /v1beta1/{ragEngineConfig.name}

                  Updates a RagEngineConfig.

                  updateSemanticGovernancePolicyEngine

                  PATCH /v1beta1/{semanticGovernancePolicyEngine.name}

                  Updates a SemanticGovernancePolicyEngine.

        REST Resource: v1beta1.projects.locations.agents

                Methods

                  create

                  POST /v1beta1/{parent}/agents

                  Creates an agent.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes an agent.

                  get

                  GET /v1beta1/{name}

                  Retrieves an agent.

                  list

                  GET /v1beta1/{parent}/agents

                  Lists the agents in a location that belong to the caller.

                  patch

                  PATCH /v1beta1/{agent.name}

                  Updates an agent.

        REST Resource: v1beta1.projects.locations.batchPredictionJobs

                Methods

                  cancel

                  POST /v1beta1/{name}:cancel

                  Cancels a BatchPredictionJob.

                  create

                  POST /v1beta1/{parent}/batchPredictionJobs

                  Creates a BatchPredictionJob.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a BatchPredictionJob.

                  get

                  GET /v1beta1/{name}

                  Gets a BatchPredictionJob

                  list

                  GET /v1beta1/{parent}/batchPredictionJobs

                  Lists BatchPredictionJobs in a Location.

        REST Resource: v1beta1.projects.locations.cachedContents

                Methods

                  create

                  POST /v1beta1/{parent}/cachedContents

                  Creates cached content, this call will initialize the cached content in the data storage, and users need to pay for the cache data storage.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes cached content

                  get

                  GET /v1beta1/{name}

                  Gets cached content configurations

                  list

                  GET /v1beta1/{parent}/cachedContents

                  Lists cached contents in a project

                  patch

                  PATCH /v1beta1/{cachedContent.name}

                  Updates cached content configurations

        REST Resource: v1beta1.projects.locations.customJobs

                Methods

                  cancel

                  POST /v1beta1/{name}:cancel

                  Cancels a CustomJob.

                  create

                  POST /v1beta1/{parent}/customJobs

                  Creates a CustomJob.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a CustomJob.

                  get

                  GET /v1beta1/{name}

                  Gets a CustomJob.

                  list

                  GET /v1beta1/{parent}/customJobs

                  Lists CustomJobs in a Location.

        REST Resource: v1beta1.projects.locations.datasets

                Methods

                  assemble

                  POST /v1beta1/{name}:assemble

                  Assembles each row of a multimodal dataset and writes the result into a BigQuery table.

                  assess

                  POST /v1beta1/{name}:assess

                  Assesses the state or validity of the dataset with respect to a given use case.

                  create

                  POST /v1beta1/{parent}/datasets

                  Creates a Dataset.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a Dataset.

                  export

                  POST /v1beta1/{name}:export

                  Exports data from a Dataset.

                  get

                  GET /v1beta1/{name}

                  Gets a Dataset.

                  import

                  POST /v1beta1/{name}:import

                  Imports data into a Dataset.

                  list

                  GET /v1beta1/{parent}/datasets

                  Lists Datasets in a Location.

                  patch

                  PATCH /v1beta1/{dataset.name}

                  Updates a Dataset.

                  searchDataItems

                  GET /v1beta1/{dataset}:searchDataItems

                  Searches DataItems in a Dataset.

        REST Resource: v1beta1.projects.locations.datasets.annotationSpecs

                Methods

                  get

                  GET /v1beta1/{name}

                  Gets an AnnotationSpec.

        REST Resource: v1beta1.projects.locations.datasets.dataItems

                Methods

                  list

                  GET /v1beta1/{parent}/dataItems

                  Lists DataItems in a Dataset.

        REST Resource: v1beta1.projects.locations.datasets.dataItems.annotations

                Methods

                  list

                  GET /v1beta1/{parent}/annotations

                  Lists Annotations belongs to a dataitem.

        REST Resource: v1beta1.projects.locations.datasets.datasetVersions

                Methods

                  create

                  POST /v1beta1/{parent}/datasetVersions

                  Create a version from a Dataset.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a Dataset version.

                  get

                  GET /v1beta1/{name}

                  Gets a Dataset version.

                  list

                  GET /v1beta1/{parent}/datasetVersions

                  Lists DatasetVersions in a Dataset.

                  patch

                  PATCH /v1beta1/{datasetVersion.name}

                  Updates a DatasetVersion.

                  restore

                  GET /v1beta1/{name}:restore

                  Restores a dataset version.

        REST Resource: v1beta1.projects.locations.datasets.savedQueries

                Methods

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a SavedQuery.

                  list

                  GET /v1beta1/{parent}/savedQueries

                  Lists SavedQueries in a Dataset.

        REST Resource: v1beta1.projects.locations.deploymentResourcePools

                Methods

                  create

                  POST /v1beta1/{parent}/deploymentResourcePools

                  Create a DeploymentResourcePool.

                  delete

                  DELETE /v1beta1/{name}

                  Delete a DeploymentResourcePool.

                  get

                  GET /v1beta1/{name}

                  Get a DeploymentResourcePool.

                  list

                  GET /v1beta1/{parent}/deploymentResourcePools

                  List DeploymentResourcePools in a location.

                  patch

                  PATCH /v1beta1/{deploymentResourcePool.name}

                  Update a DeploymentResourcePool.

                  queryDeployedModels

                  GET /v1beta1/{deploymentResourcePool}:queryDeployedModels

                  List DeployedModels that have been deployed on this DeploymentResourcePool.

        REST Resource: v1beta1.projects.locations.endpoints

                Methods

                  computeTokens

                  POST /v1beta1/{endpoint}:computeTokens

                  Return a list of tokens based on the input text.

                  countTokens

                  POST /v1beta1/{endpoint}:countTokens

                  Perform a token counting.

                  create

                  POST /v1beta1/{parent}/endpoints

                  Creates an Endpoint.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes an Endpoint.

                  deployModel

                  POST /v1beta1/{endpoint}:deployModel

                  Deploys a Model into this Endpoint, creating a DeployedModel within it.

                  directPredict

                  POST /v1beta1/{endpoint}:directPredict

                  Perform an unary online prediction request to a gRPC model server for Vertex first-party products and frameworks.

                  directRawPredict

                  POST /v1beta1/{endpoint}:directRawPredict

                  Perform an unary online prediction request to a gRPC model server for custom containers.

                  explain

                  POST /v1beta1/{endpoint}:explain

                  Perform an online explanation.

                  generateContent

                  POST /v1beta1/{model}:generateContent

                  Generate content with multimodal inputs.

                  get

                  GET /v1beta1/{name}

                  Gets an Endpoint.

                  getIamPolicy

                  POST /v1beta1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1beta1/{parent}/endpoints

                  Lists Endpoints in a Location.

                  mutateDeployedModel

                  POST /v1beta1/{endpoint}:mutateDeployedModel

                  Updates an existing deployed model.

                  patch

                  PATCH /v1beta1/{endpoint.name}

                  Updates an Endpoint.

                  predict

                  POST /v1beta1/{endpoint}:predict

                  Perform an online inference.

                  predictLongRunning

                  POST /v1beta1/{endpoint}:predictLongRunning

                  rawPredict

                  POST /v1beta1/{endpoint}:rawPredict

                  Perform an online prediction with an arbitrary HTTP payload.

                  serverStreamingPredict

                  POST /v1beta1/{endpoint}:serverStreamingPredict

                  Perform a server-side streaming online prediction request for Vertex LLM streaming.

                  setIamPolicy

                  POST /v1beta1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  streamGenerateContent

                  POST /v1beta1/{model}:streamGenerateContent

                  Generate content with multimodal inputs with streaming support.

                  streamRawPredict

                  POST /v1beta1/{endpoint}:streamRawPredict

                  Perform a streaming online prediction with an arbitrary HTTP payload.

                  testIamPermissions

                  POST /v1beta1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

                  undeployModel

                  POST /v1beta1/{endpoint}:undeployModel

                  Undeploys a Model from an Endpoint, removing a DeployedModel from it, and freeing all resources it's using.

                  update

                  POST /v1beta1/{endpoint.name}:update

                  Updates an Endpoint with a long running operation.

        REST Resource: v1beta1.projects.locations.endpoints.chat

                Methods

                  completions

                  POST /v1beta1/{endpoint}/chat/completions

                  Exposes an OpenAI-compatible endpoint for chat completions.

        REST Resource: v1beta1.projects.locations.endpoints.responses

                Methods

                  delete

                  DELETE /v1beta1/{name}

                  Deletes the response from the endpoint.

                  get

                  GET /v1beta1/{name}

                  Gets the response from the endpoint.

        REST Resource: v1beta1.projects.locations.exampleStores

                Methods

                  create

                  POST /v1beta1/{parent}/exampleStores

                  Create an ExampleStore.

                  delete

                  DELETE /v1beta1/{name}

                  Delete an ExampleStore.

                  fetchExamples

                  POST /v1beta1/{exampleStore}:fetchExamples

                  Get Examples from the Example Store.

                  get

                  GET /v1beta1/{name}

                  Get an ExampleStore.

                  list

                  GET /v1beta1/{parent}/exampleStores

                  List ExampleStores in a Location.

                  patch

                  PATCH /v1beta1/{exampleStore.name}

                  Update an ExampleStore.

                  removeExamples

                  POST /v1beta1/{exampleStore}:removeExamples

                  Remove Examples from the Example Store.

                  searchExamples

                  POST /v1beta1/{exampleStore}:searchExamples

                  Search for similar Examples for given selection criteria.

                  upsertExamples

                  POST /v1beta1/{exampleStore}:upsertExamples

                  Create or update Examples in the Example Store.

        REST Resource: v1beta1.projects.locations.extensions

                Methods

                  delete

                  DELETE /v1beta1/{name}

                  Deletes an Extension.

                  execute

                  POST /v1beta1/{name}:execute

                  Executes the request against a given extension.

                  get

                  GET /v1beta1/{name}

                  Gets an Extension.

                  import

                  POST /v1beta1/{parent}/extensions:import

                  Imports an Extension.

                  list

                  GET /v1beta1/{parent}/extensions

                  Lists Extensions in a location.

                  patch

                  PATCH /v1beta1/{extension.name}

                  Updates an Extension.

                  query

                  POST /v1beta1/{name}:query

                  Queries an extension with a default controller.

        REST Resource: v1beta1.projects.locations.featureGroups

                Methods

                  create

                  POST /v1beta1/{parent}/featureGroups

                  Creates a new FeatureGroup in a given project and location.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a single FeatureGroup.

                  get

                  GET /v1beta1/{name}

                  Gets details of a single FeatureGroup.

                  getIamPolicy

                  POST /v1beta1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1beta1/{parent}/featureGroups

                  Lists FeatureGroups in a given project and location.

                  patch

                  PATCH /v1beta1/{featureGroup.name}

                  Updates the parameters of a single FeatureGroup.

                  setIamPolicy

                  POST /v1beta1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  testIamPermissions

                  POST /v1beta1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1beta1.projects.locations.featureGroups.featureMonitors

                Methods

                  create

                  POST /v1beta1/{parent}/featureMonitors

                  Creates a new FeatureMonitor in a given project, location and FeatureGroup.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a single FeatureMonitor.

                  get

                  GET /v1beta1/{name}

                  Gets details of a single FeatureMonitor.

                  list

                  GET /v1beta1/{parent}/featureMonitors

                  Lists FeatureGroups in a given project and location.

                  patch

                  PATCH /v1beta1/{featureMonitor.name}

                  Updates the parameters of a single FeatureMonitor.

        REST Resource: v1beta1.projects.locations.featureGroups.featureMonitors.featureMonitorJobs

                Methods

                  create

                  POST /v1beta1/{parent}/featureMonitorJobs

                  Creates a new feature monitor job.

                  get

                  GET /v1beta1/{name}

                  Get a feature monitor job.

                  list

                  GET /v1beta1/{parent}/featureMonitorJobs

                  List feature monitor jobs.

        REST Resource: v1beta1.projects.locations.featureGroups.features

                Methods

                  batchCreate

                  POST /v1beta1/{parent}/features:batchCreate

                  Creates a batch of Features in a given FeatureGroup.

                  create

                  POST /v1beta1/{parent}/features

                  Creates a new Feature in a given FeatureGroup.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a single Feature.

                  get

                  GET /v1beta1/{name}

                  Gets details of a single Feature.

                  list

                  GET /v1beta1/{parent}/features

                  Lists Features in a given FeatureGroup.

                  patch

                  PATCH /v1beta1/{feature.name}

                  Updates the parameters of a single Feature.

        REST Resource: v1beta1.projects.locations.featureOnlineStores

                Methods

                  create

                  POST /v1beta1/{parent}/featureOnlineStores

                  Creates a new FeatureOnlineStore in a given project and location.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a single FeatureOnlineStore.

                  get

                  GET /v1beta1/{name}

                  Gets details of a single FeatureOnlineStore.

                  getIamPolicy

                  POST /v1beta1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1beta1/{parent}/featureOnlineStores

                  Lists FeatureOnlineStores in a given project and location.

                  patch

                  PATCH /v1beta1/{featureOnlineStore.name}

                  Updates the parameters of a single FeatureOnlineStore.

                  setIamPolicy

                  POST /v1beta1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  testIamPermissions

                  POST /v1beta1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1beta1.projects.locations.featureOnlineStores.featureViews

                Methods

                  create

                  POST /v1beta1/{parent}/featureViews

                  Creates a new FeatureView in a given FeatureOnlineStore.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a single FeatureView.

                  directWrite

                  POST /v1beta1/{featureView}:directWrite

                  Bidirectional streaming RPC to directly write to feature values in a feature view.

                  fetchFeatureValues

                  POST /v1beta1/{featureView}:fetchFeatureValues

                  Fetch feature values under a FeatureView.

                  generateFetchAccessToken

                  POST /v1beta1/{featureView}:generateFetchAccessToken

                  RPC to generate an access token for the given feature view.

                  get

                  GET /v1beta1/{name}

                  Gets details of a single FeatureView.

                  getIamPolicy

                  POST /v1beta1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1beta1/{parent}/featureViews

                  Lists FeatureViews in a given FeatureOnlineStore.

                  patch

                  PATCH /v1beta1/{featureView.name}

                  Updates the parameters of a single FeatureView.

                  searchNearestEntities

                  POST /v1beta1/{featureView}:searchNearestEntities

                  Search the nearest entities under a FeatureView.

                  setIamPolicy

                  POST /v1beta1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  streamingFetchFeatureValues

                  POST /v1beta1/{featureView}:streamingFetchFeatureValues

                  Bidirectional streaming RPC to fetch feature values under a FeatureView.

                  sync

                  POST /v1beta1/{featureView}:sync

                  Triggers on-demand sync for the FeatureView.

                  testIamPermissions

                  POST /v1beta1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1beta1.projects.locations.featureOnlineStores.featureViews.featureViewSyncs

                Methods

                  get

                  GET /v1beta1/{name}

                  Gets details of a single FeatureViewSync.

                  list

                  GET /v1beta1/{parent}/featureViewSyncs

                  Lists FeatureViewSyncs in a given FeatureView.

        REST Resource: v1beta1.projects.locations.featurestores

                Methods

                  batchReadFeatureValues

                  POST /v1beta1/{featurestore}:batchReadFeatureValues

                  Batch reads Feature values from a Featurestore.

                  create

                  POST /v1beta1/{parent}/featurestores

                  Creates a new Featurestore in a given project and location.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a single Featurestore.

                  get

                  GET /v1beta1/{name}

                  Gets details of a single Featurestore.

                  getIamPolicy

                  POST /v1beta1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1beta1/{parent}/featurestores

                  Lists Featurestores in a given project and location.

                  patch

                  PATCH /v1beta1/{featurestore.name}

                  Updates the parameters of a single Featurestore.

                  searchFeatures

                  GET /v1beta1/{location}/featurestores:searchFeatures

                  Searches Features matching a query in a given project.

                  setIamPolicy

                  POST /v1beta1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  testIamPermissions

                  POST /v1beta1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1beta1.projects.locations.featurestores.entityTypes

                Methods

                  create

                  POST /v1beta1/{parent}/entityTypes

                  Creates a new EntityType in a given Featurestore.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a single EntityType.

                  deleteFeatureValues

                  POST /v1beta1/{entityType}:deleteFeatureValues

                  Delete Feature values from Featurestore.

                  exportFeatureValues

                  POST /v1beta1/{entityType}:exportFeatureValues

                  Exports Feature values from all the entities of a target EntityType.

                  get

                  GET /v1beta1/{name}

                  Gets details of a single EntityType.

                  getIamPolicy

                  POST /v1beta1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  importFeatureValues

                  POST /v1beta1/{entityType}:importFeatureValues

                  Imports Feature values into the Featurestore from a source storage.

                  list

                  GET /v1beta1/{parent}/entityTypes

                  Lists EntityTypes in a given Featurestore.

                  patch

                  PATCH /v1beta1/{entityType.name}

                  Updates the parameters of a single EntityType.

                  readFeatureValues

                  POST /v1beta1/{entityType}:readFeatureValues

                  Reads Feature values of a specific entity of an EntityType.

                  setIamPolicy

                  POST /v1beta1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  streamingReadFeatureValues

                  POST /v1beta1/{entityType}:streamingReadFeatureValues

                  Reads Feature values for multiple entities.

                  testIamPermissions

                  POST /v1beta1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

                  writeFeatureValues

                  POST /v1beta1/{entityType}:writeFeatureValues

                  Writes Feature values of one or more entities of an EntityType.

        REST Resource: v1beta1.projects.locations.featurestores.entityTypes.features

                Methods

                  batchCreate

                  POST /v1beta1/{parent}/features:batchCreate

                  Creates a batch of Features in a given EntityType.

                  create

                  POST /v1beta1/{parent}/features

                  Creates a new Feature in a given EntityType.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a single Feature.

                  get

                  GET /v1beta1/{name}

                  Gets details of a single Feature.

                  list

                  GET /v1beta1/{parent}/features

                  Lists Features in a given EntityType.

                  patch

                  PATCH /v1beta1/{feature.name}

                  Updates the parameters of a single Feature.

        REST Resource: v1beta1.projects.locations.hyperparameterTuningJobs

                Methods

                  cancel

                  POST /v1beta1/{name}:cancel

                  Cancels a HyperparameterTuningJob.

                  create

                  POST /v1beta1/{parent}/hyperparameterTuningJobs

                  Creates a HyperparameterTuningJob

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a HyperparameterTuningJob.

                  get

                  GET /v1beta1/{name}

                  Gets a HyperparameterTuningJob

                  list

                  GET /v1beta1/{parent}/hyperparameterTuningJobs

                  Lists HyperparameterTuningJobs in a Location.

        REST Resource: v1beta1.projects.locations.indexEndpoints

                Methods

                  create

                  POST /v1beta1/{parent}/indexEndpoints

                  Creates an IndexEndpoint.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes an IndexEndpoint.

                  deployIndex

                  POST /v1beta1/{indexEndpoint}:deployIndex

                  Deploys an Index into this IndexEndpoint, creating a DeployedIndex within it.

                  get

                  GET /v1beta1/{name}

                  Gets an IndexEndpoint.

                  list

                  GET /v1beta1/{parent}/indexEndpoints

                  Lists IndexEndpoints in a Location.

                  mutateDeployedIndex

                  POST /v1beta1/{indexEndpoint}:mutateDeployedIndex

                  Update an existing DeployedIndex under an IndexEndpoint.

                  patch

                  PATCH /v1beta1/{indexEndpoint.name}

                  Updates an IndexEndpoint.

                  undeployIndex

                  POST /v1beta1/{indexEndpoint}:undeployIndex

                  Undeploys an Index from an IndexEndpoint, removing a DeployedIndex from it, and freeing all resources it's using.

        REST Resource: v1beta1.projects.locations.indexes

                Methods

                  create

                  POST /v1beta1/{parent}/indexes

                  Creates an Index.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes an Index.

                  get

                  GET /v1beta1/{name}

                  Gets an Index.

                  import

                  POST /v1beta1/{name}:import

                  Imports an Index from an external source (e.g., BigQuery).

                  list

                  GET /v1beta1/{parent}/indexes

                  Lists Indexes in a Location.

                  patch

                  PATCH /v1beta1/{index.name}

                  Updates an Index.

                  removeDatapoints

                  POST /v1beta1/{index}:removeDatapoints

                  Remove Datapoints from an Index.

                  upsertDatapoints

                  POST /v1beta1/{index}:upsertDatapoints

                  Add/update Datapoints into an Index.

        REST Resource: v1beta1.projects.locations.interactions

                Methods

                  createStream

                  POST /v1beta1/projects/*/locations/*/interactions:createStream

                  Creates an interaction and streams the response.

                  delete
(deprecated)

                  DELETE /v1beta1/{name}

                  Deletes an interaction.

        REST Resource: v1beta1.projects.locations.interactionsHttp

                Methods

                  cancel

                  POST /v1beta1/{name}/cancel

                  Cancels an interaction.

                  create

                  POST /v1beta1/{parent}/interactionsHttp

                  Generates a set of responses from the model.

                  get

                  GET /v1beta1/{name}

                  Gets an interaction.

        REST Resource: v1beta1.projects.locations.memoryBanks

                Methods

                  ingestEvents

                  POST /v1beta1/{parent}:ingestEvents

                  Ingests events for a Memory Bank.

        REST Resource: v1beta1.projects.locations.memoryBanks.memories

                Methods

                  create

                  POST /v1beta1/{parent}/memories

                  Create a Memory.

                  delete

                  DELETE /v1beta1/{name}

                  Delete a Memory.

                  generate

                  POST /v1beta1/{parent}/memories:generate

                  Generate memories.

                  get

                  GET /v1beta1/{name}

                  Get a Memory.

                  list

                  GET /v1beta1/{parent}/memories

                  List Memories.

                  patch

                  PATCH /v1beta1/{memory.name}

                  Update a Memory.

                  retrieve

                  POST /v1beta1/{parent}/memories:retrieve

                  Retrieve memories.

                  retrieveProfiles

                  POST /v1beta1/{parent}/memories:retrieveProfiles

                  Retrieves profiles.

        REST Resource: v1beta1.projects.locations.metadataStores

                Methods

                  create

                  POST /v1beta1/{parent}/metadataStores

                  Initializes a MetadataStore, including allocation of resources.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a single MetadataStore and all its child resources (Artifacts, Executions, and Contexts).

                  get

                  GET /v1beta1/{name}

                  Retrieves a specific MetadataStore.

                  list

                  GET /v1beta1/{parent}/metadataStores

                  Lists MetadataStores for a Location.

        REST Resource: v1beta1.projects.locations.metadataStores.artifacts

                Methods

                  create

                  POST /v1beta1/{parent}/artifacts

                  Creates an Artifact associated with a MetadataStore.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes an Artifact.

                  get

                  GET /v1beta1/{name}

                  Retrieves a specific Artifact.

                  list

                  GET /v1beta1/{parent}/artifacts

                  Lists Artifacts in the MetadataStore.

                  patch

                  PATCH /v1beta1/{artifact.name}

                  Updates a stored Artifact.

                  purge

                  POST /v1beta1/{parent}/artifacts:purge

                  Purges Artifacts.

                  queryArtifactLineageSubgraph

                  GET /v1beta1/{artifact}:queryArtifactLineageSubgraph

                  Retrieves lineage of an Artifact represented through Artifacts and Executions connected by Event edges and returned as a LineageSubgraph.

        REST Resource: v1beta1.projects.locations.metadataStores.contexts

                Methods

                  addContextArtifactsAndExecutions

                  POST /v1beta1/{context}:addContextArtifactsAndExecutions

                  Adds a set of Artifacts and Executions to a Context.

                  addContextChildren

                  POST /v1beta1/{context}:addContextChildren

                  Adds a set of Contexts as children to a parent Context.

                  create

                  POST /v1beta1/{parent}/contexts

                  Creates a Context associated with a MetadataStore.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a stored Context.

                  get

                  GET /v1beta1/{name}

                  Retrieves a specific Context.

                  list

                  GET /v1beta1/{parent}/contexts

                  Lists Contexts on the MetadataStore.

                  patch

                  PATCH /v1beta1/{context.name}

                  Updates a stored Context.

                  purge

                  POST /v1beta1/{parent}/contexts:purge

                  Purges Contexts.

                  queryContextLineageSubgraph

                  GET /v1beta1/{context}:queryContextLineageSubgraph

                  Retrieves Artifacts and Executions within the specified Context, connected by Event edges and returned as a LineageSubgraph.

                  removeContextChildren

                  POST /v1beta1/{context}:removeContextChildren

                  Remove a set of children contexts from a parent Context.

        REST Resource: v1beta1.projects.locations.metadataStores.executions

                Methods

                  addExecutionEvents

                  POST /v1beta1/{execution}:addExecutionEvents

                  Adds Events to the specified Execution.

                  create

                  POST /v1beta1/{parent}/executions

                  Creates an Execution associated with a MetadataStore.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes an Execution.

                  get

                  GET /v1beta1/{name}

                  Retrieves a specific Execution.

                  list

                  GET /v1beta1/{parent}/executions

                  Lists Executions in the MetadataStore.

                  patch

                  PATCH /v1beta1/{execution.name}

                  Updates a stored Execution.

                  purge

                  POST /v1beta1/{parent}/executions:purge

                  Purges Executions.

                  queryExecutionInputsAndOutputs

                  GET /v1beta1/{execution}:queryExecutionInputsAndOutputs

                  Obtains the set of input and output Artifacts for this Execution, in the form of LineageSubgraph that also contains the Execution and connecting Events.

        REST Resource: v1beta1.projects.locations.metadataStores.metadataSchemas

                Methods

                  create

                  POST /v1beta1/{parent}/metadataSchemas

                  Creates a MetadataSchema.

                  get

                  GET /v1beta1/{name}

                  Retrieves a specific MetadataSchema.

                  list

                  GET /v1beta1/{parent}/metadataSchemas

                  Lists MetadataSchemas.

        REST Resource: v1beta1.projects.locations.migratableResources

                Methods

                  batchMigrate

                  POST /v1beta1/{parent}/migratableResources:batchMigrate

                  Batch migrates resources from ml.googleapis.com, automl.googleapis.com, and datalabeling.googleapis.com to Agent Platform.

                  search

                  POST /v1beta1/{parent}/migratableResources:search

                  Searches all of the resources in automl.googleapis.com, datalabeling.googleapis.com and ml.googleapis.com that can be migrated to Agent Platform's given location.

        REST Resource: v1beta1.projects.locations.modelDeploymentMonitoringJobs

                Methods

                  create

                  POST /v1beta1/{parent}/modelDeploymentMonitoringJobs

                  Creates a ModelDeploymentMonitoringJob.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a ModelDeploymentMonitoringJob.

                  get

                  GET /v1beta1/{name}

                  Gets a ModelDeploymentMonitoringJob.

                  list

                  GET /v1beta1/{parent}/modelDeploymentMonitoringJobs

                  Lists ModelDeploymentMonitoringJobs in a Location.

                  patch

                  PATCH /v1beta1/{modelDeploymentMonitoringJob.name}

                  Updates a ModelDeploymentMonitoringJob.

                  pause

                  POST /v1beta1/{name}:pause

                  Pauses a ModelDeploymentMonitoringJob.

                  resume

                  POST /v1beta1/{name}:resume

                  Resumes a paused ModelDeploymentMonitoringJob.

                  searchModelDeploymentMonitoringStatsAnomalies

                  POST /v1beta1/{modelDeploymentMonitoringJob}:searchModelDeploymentMonitoringStatsAnomalies

                  Searches Model Monitoring Statistics generated within a given time window.

        REST Resource: v1beta1.projects.locations.modelMonitors

                Methods

                  create

                  POST /v1beta1/{parent}/modelMonitors

                  Creates a ModelMonitor.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a ModelMonitor.

                  get

                  GET /v1beta1/{name}

                  Gets a ModelMonitor.

                  list

                  GET /v1beta1/{parent}/modelMonitors

                  Lists ModelMonitors in a Location.

                  patch

                  PATCH /v1beta1/{modelMonitor.name}

                  Updates a ModelMonitor.

                  searchModelMonitoringAlerts

                  POST /v1beta1/{modelMonitor}:searchModelMonitoringAlerts

                  Returns the Model Monitoring alerts.

                  searchModelMonitoringStats

                  POST /v1beta1/{modelMonitor}:searchModelMonitoringStats

                  Searches Model Monitoring Stats generated within a given time window.

        REST Resource: v1beta1.projects.locations.modelMonitors.modelMonitoringJobs

                Methods

                  create

                  POST /v1beta1/{parent}/modelMonitoringJobs

                  Creates a ModelMonitoringJob.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a ModelMonitoringJob.

                  get

                  GET /v1beta1/{name}

                  Gets a ModelMonitoringJob.

                  list

                  GET /v1beta1/{parent}/modelMonitoringJobs

                  Lists ModelMonitoringJobs.

        REST Resource: v1beta1.projects.locations.models

                Methods

                  copy

                  POST /v1beta1/{parent}/models:copy

                  Copies an already existing Agent Platform Model into the specified Location.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a Model.

                  deleteVersion

                  DELETE /v1beta1/{name}:deleteVersion

                  Deletes a Model version.

                  export

                  POST /v1beta1/{name}:export

                  Exports a trained, exportable Model to a location specified by the user.

                  get

                  GET /v1beta1/{name}

                  Gets a Model.

                  getIamPolicy

                  POST /v1beta1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1beta1/{parent}/models

                  Lists Models in a Location.

                  listCheckpoints

                  GET /v1beta1/{name}:listCheckpoints

                  Lists checkpoints of the specified model version.

                  listVersions

                  GET /v1beta1/{name}:listVersions

                  Lists versions of the specified model.

                  mergeVersionAliases

                  POST /v1beta1/{name}:mergeVersionAliases

                  Merges a set of aliases for a Model version.

                  patch

                  PATCH /v1beta1/{model.name}

                  Updates a Model.

                  setIamPolicy

                  POST /v1beta1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  testIamPermissions

                  POST /v1beta1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

                  updateExplanationDataset

                  POST /v1beta1/{model}:updateExplanationDataset

                  Incrementally update the dataset used for an examples model.

                  upload

                  POST /v1beta1/{parent}/models:upload

                  Uploads a Model artifact into Agent Platform.

        REST Resource: v1beta1.projects.locations.models.evaluations

                Methods

                  get

                  GET /v1beta1/{name}

                  Gets a ModelEvaluation.

                  import

                  POST /v1beta1/{parent}/evaluations:import

                  Imports an externally generated ModelEvaluation.

                  list

                  GET /v1beta1/{parent}/evaluations

                  Lists ModelEvaluations in a Model.

        REST Resource: v1beta1.projects.locations.models.evaluations.slices

                Methods

                  batchImport

                  POST /v1beta1/{parent}:batchImport

                  Imports a list of externally generated EvaluatedAnnotations.

                  get

                  GET /v1beta1/{name}

                  Gets a ModelEvaluationSlice.

                  list

                  GET /v1beta1/{parent}/slices

                  Lists ModelEvaluationSlices in a ModelEvaluation.

        REST Resource: v1beta1.projects.locations.notebookExecutionJobs

                Methods

                  create

                  POST /v1beta1/{parent}/notebookExecutionJobs

                  Creates a NotebookExecutionJob.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a NotebookExecutionJob.

                  get

                  GET /v1beta1/{name}

                  Gets a NotebookExecutionJob.

                  list

                  GET /v1beta1/{parent}/notebookExecutionJobs

                  Lists NotebookExecutionJobs in a Location.

        REST Resource: v1beta1.projects.locations.notebookRuntimeTemplates

                Methods

                  create

                  POST /v1beta1/{parent}/notebookRuntimeTemplates

                  Creates a NotebookRuntimeTemplate.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a NotebookRuntimeTemplate.

                  get

                  GET /v1beta1/{name}

                  Gets a NotebookRuntimeTemplate.

                  getIamPolicy

                  POST /v1beta1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1beta1/{parent}/notebookRuntimeTemplates

                  Lists NotebookRuntimeTemplates in a Location.

                  patch

                  PATCH /v1beta1/{notebookRuntimeTemplate.name}

                  Updates a NotebookRuntimeTemplate.

                  setIamPolicy

                  POST /v1beta1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  testIamPermissions

                  POST /v1beta1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1beta1.projects.locations.notebookRuntimes

                Methods

                  assign

                  POST /v1beta1/{parent}/notebookRuntimes:assign

                  Assigns a NotebookRuntime to a user for a particular Notebook file.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a NotebookRuntime.

                  get

                  GET /v1beta1/{name}

                  Gets a NotebookRuntime.

                  list

                  GET /v1beta1/{parent}/notebookRuntimes

                  Lists NotebookRuntimes in a Location.

                  start

                  POST /v1beta1/{name}:start

                  Starts a NotebookRuntime.

                  stop

                  POST /v1beta1/{name}:stop

                  Stops a NotebookRuntime.

                  upgrade

                  POST /v1beta1/{name}:upgrade

                  Upgrades a NotebookRuntime.

        REST Resource: v1beta1.projects.locations.onlineEvaluators

                Methods

                  activate

                  POST /v1beta1/{name}:activate

                  Activates an OnlineEvaluator.

                  create

                  POST /v1beta1/{parent}/onlineEvaluators

                  Creates an OnlineEvaluator in the given project and location.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes an OnlineEvaluator.

                  get

                  GET /v1beta1/{name}

                  Gets details of an OnlineEvaluator.

                  list

                  GET /v1beta1/{parent}/onlineEvaluators

                  Lists the OnlineEvaluators for the given project and location.

                  patch

                  PATCH /v1beta1/{onlineEvaluator.name}

                  Updates the fields of an OnlineEvaluator.

                  suspend

                  POST /v1beta1/{name}:suspend

                  Suspends an OnlineEvaluator.

        REST Resource: v1beta1.projects.locations.operations

                Methods

                  cancel

                  POST /v1beta1/{name}:cancel

                  Starts asynchronous cancellation on a long-running operation.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a long-running operation.

                  get

                  GET /v1beta1/{name}

                  Gets the latest state of a long-running operation.

                  list

                  GET /v1beta1/{name}/operations

                  Lists operations that match the specified filter in the request.

                  wait

                  POST /v1beta1/{name}:wait

                  Waits until the specified long-running operation is done or reaches at most a specified timeout, returning the latest state.

        REST Resource: v1beta1.projects.locations.persistentResources

                Methods

                  create

                  POST /v1beta1/{parent}/persistentResources

                  Creates a PersistentResource.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a PersistentResource.

                  get

                  GET /v1beta1/{name}

                  Gets a PersistentResource.

                  list

                  GET /v1beta1/{parent}/persistentResources

                  Lists PersistentResources in a Location.

                  patch

                  PATCH /v1beta1/{persistentResource.name}

                  Updates a PersistentResource.

                  reboot

                  POST /v1beta1/{name}:reboot

                  Reboots a PersistentResource.

        REST Resource: v1beta1.projects.locations.pipelineJobs

                Methods

                  batchCancel

                  POST /v1beta1/{parent}/pipelineJobs:batchCancel

                  Batch cancel PipelineJobs.

                  batchDelete

                  POST /v1beta1/{parent}/pipelineJobs:batchDelete

                  Batch deletes PipelineJobs The Operation is atomic.

                  cancel

                  POST /v1beta1/{name}:cancel

                  Cancels a PipelineJob.

                  create

                  POST /v1beta1/{parent}/pipelineJobs

                  Creates a PipelineJob.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a PipelineJob.

                  get

                  GET /v1beta1/{name}

                  Gets a PipelineJob.

                  list

                  GET /v1beta1/{parent}/pipelineJobs

                  Lists PipelineJobs in a Location.

        REST Resource: v1beta1.projects.locations.publishers.models

                Methods

                  computeTokens

                  POST /v1beta1/{endpoint}:computeTokens

                  Return a list of tokens based on the input text.

                  countTokens

                  POST /v1beta1/{endpoint}:countTokens

                  Perform a token counting.

                  embedContent

                  POST /v1beta1/{model}:embedContent

                  Embed content with multimodal inputs.

                  export

                  POST /v1beta1/{parent}/{name}:export

                  Exports a publisher model to a user provided Google Cloud Storage bucket.

                  fetchPublisherModelConfig

                  GET /v1beta1/{name}:fetchPublisherModelConfig

                  Fetches the configs of publisher models.

                  generateContent

                  POST /v1beta1/{model}:generateContent

                  Generate content with multimodal inputs.

                  getIamPolicy

                  POST /v1beta1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  predict

                  POST /v1beta1/{endpoint}:predict

                  Perform an online inference.

                  predictLongRunning

                  POST /v1beta1/{endpoint}:predictLongRunning

                  rawPredict

                  POST /v1beta1/{endpoint}:rawPredict

                  Perform an online prediction with an arbitrary HTTP payload.

                  serverStreamingPredict

                  POST /v1beta1/{endpoint}:serverStreamingPredict

                  Perform a server-side streaming online prediction request for Vertex LLM streaming.

                  setPublisherModelConfig

                  POST /v1beta1/{name}:setPublisherModelConfig

                  Sets (creates or updates) configs of publisher models.

                  streamGenerateContent

                  POST /v1beta1/{model}:streamGenerateContent

                  Generate content with multimodal inputs with streaming support.

                  streamRawPredict

                  POST /v1beta1/{endpoint}:streamRawPredict

                  Perform a streaming online prediction with an arbitrary HTTP payload.

        REST Resource: v1beta1.projects.locations.publishers.v1.responses

                Methods

                  delete

                  DELETE /v1beta1/{name}

                  Deletes the response from the endpoint.

                  get

                  GET /v1beta1/{name}

                  Gets the response from the endpoint.

        REST Resource: v1beta1.projects.locations.ragCorpora

                Methods

                  create

                  POST /v1beta1/{parent}/ragCorpora

                  Creates a RagCorpus.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a RagCorpus.

                  get

                  GET /v1beta1/{name}

                  Gets a RagCorpus.

                  list

                  GET /v1beta1/{parent}/ragCorpora

                  Lists RagCorpora in a Location.

                  patch

                  PATCH /v1beta1/{ragCorpus.name}

                  Updates a RagCorpus.

        REST Resource: v1beta1.projects.locations.ragCorpora.ragDataSchemas

                Methods

                  batchCreate

                  POST /v1beta1/{parent}/ragDataSchemas:batchCreate

                  Batch Create one or more RagDataSchemas

                  batchDelete

                  POST /v1beta1/{parent}/ragDataSchemas:batchDelete

                  Batch Deletes one or more RagDataSchemas

                  create

                  POST /v1beta1/{parent}/ragDataSchemas

                  Creates a RagDataSchema.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a RagDataSchema.

                  get

                  GET /v1beta1/{name}

                  Gets a RagDataSchema.

                  list

                  GET /v1beta1/{parent}/ragDataSchemas

                  Lists RagDataSchemas in a Location.

        REST Resource: v1beta1.projects.locations.ragCorpora.ragFiles

                Methods

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a RagFile.

                  get

                  GET /v1beta1/{name}

                  Gets a RagFile.

                  import

                  POST /v1beta1/{parent}/ragFiles:import

                  Import files from Google Cloud Storage or Google Drive into a RagCorpus.

                  list

                  GET /v1beta1/{parent}/ragFiles

                  Lists RagFiles in a RagCorpus.

        REST Resource: v1beta1.projects.locations.ragCorpora.ragFiles.ragMetadata

                Methods

                  batchCreate

                  POST /v1beta1/{parent}/ragMetadata:batchCreate

                  Batch Create one or more RagMetadatas

                  batchDelete

                  POST /v1beta1/{parent}/ragMetadata:batchDelete

                  Batch Deletes one or more RagMetadata.

                  create

                  POST /v1beta1/{parent}/ragMetadata

                  Creates a RagMetadata.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a RagMetadata.

                  get

                  GET /v1beta1/{name}

                  Gets a RagMetadata.

                  list

                  GET /v1beta1/{parent}/ragMetadata

                  Lists RagMetadata in a RagFile.

                  patch

                  PATCH /v1beta1/{ragMetadata.name}

                  Updates a RagMetadata.

        REST Resource: v1beta1.projects.locations.reasoningEngines

                Methods

                  asyncQuery

                  POST /v1beta1/{name}:asyncQuery

                  Async query using a reasoning engine.

                  cancelAsyncQuery

                  POST /v1beta1/{name}:cancelAsyncQuery

                  Cancels an AsyncQueryReasoningEngine operation.

                  create

                  POST /v1beta1/{parent}/reasoningEngines

                  Creates a reasoning engine.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a reasoning engine.

                  executeCode

                  POST /v1beta1/{name}:executeCode

                  Executes code statelessly.

                  get

                  GET /v1beta1/{name}

                  Gets a reasoning engine.

                  getIamPolicy

                  POST /v1beta1/{resource}:getIamPolicy

                  Gets the access control policy for a resource.

                  list

                  GET /v1beta1/{parent}/reasoningEngines

                  Lists reasoning engines in a location.

                  patch

                  PATCH /v1beta1/{reasoningEngine.name}

                  Updates a reasoning engine.

                  query

                  POST /v1beta1/{name}:query

                  Queries using a reasoning engine.

                  setIamPolicy

                  POST /v1beta1/{resource}:setIamPolicy

                  Sets the access control policy on the specified resource.

                  streamQuery

                  POST /v1beta1/{name}:streamQuery

                  Streams queries using a reasoning engine.

                  testIamPermissions

                  POST /v1beta1/{resource}:testIamPermissions

                  Returns permissions that a caller has on the specified resource.

        REST Resource: v1beta1.projects.locations.reasoningEngines.feedbackEntries

                Methods

                  create

                  POST /v1beta1/{parent}/feedbackEntries

                  Creates a new FeedbackEntry.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a FeedbackEntry and its associated FeedbackContext.

                  get

                  GET /v1beta1/{name}

                  Retrieves a single FeedbackEntry by its resource name.

                  getFeedbackContext

                  GET /v1beta1/{name}

                  Retrieves the FeedbackContext associated with a FeedbackEntry.

                  list

                  GET /v1beta1/{parent}/feedbackEntries

                  Lists FeedbackEntries in a ReasoningEngine.

                  patch

                  PATCH /v1beta1/{feedbackEntry.name}

                  Updates an existing FeedbackEntry.

                  updateFeedbackContext

                  PATCH /v1beta1/{feedbackContext.name}

                  Updates the FeedbackContext associated with a FeedbackEntry.

        REST Resource: v1beta1.projects.locations.reasoningEngines.memories

                Methods

                  create

                  POST /v1beta1/{parent}/memories

                  Create a Memory.

                  delete

                  DELETE /v1beta1/{name}

                  Delete a Memory.

                  generate

                  POST /v1beta1/{parent}/memories:generate

                  Generate memories.

                  get

                  GET /v1beta1/{name}

                  Get a Memory.

                  ingestEvents

                  POST /v1beta1/{parent}/memories:ingestEvents

                  Ingests events for a Memory Bank.

                  list

                  GET /v1beta1/{parent}/memories

                  List Memories.

                  patch

                  PATCH /v1beta1/{memory.name}

                  Update a Memory.

                  retrieve

                  POST /v1beta1/{parent}/memories:retrieve

                  Retrieve memories.

                  retrieveProfiles

                  POST /v1beta1/{parent}/memories:retrieveProfiles

                  Retrieves profiles.

        REST Resource: v1beta1.projects.locations.reasoningEngines.runtimeRevisions

                Methods

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a reasoning engine revision.

                  get

                  GET /v1beta1/{name}

                  Gets a reasoning engine runtime revision.

                  list

                  GET /v1beta1/{parent}/runtimeRevisions

                  Lists runtime revisions in a reasoning engine.

                  query

                  POST /v1beta1/{name}:query

                  Queries using a reasoning engine.

                  streamQuery

                  POST /v1beta1/{name}:streamQuery

                  Streams queries using a reasoning engine.

        REST Resource: v1beta1.projects.locations.reasoningEngines.sandboxEnvironmentSnapshots

                Methods

                  delete

                  DELETE /v1beta1/{name}

                  Deletes the specific SandboxEnvironmentSnapshot.

                  get

                  GET /v1beta1/{name}

                  Gets details of the specific SandboxEnvironmentSnapshot.

                  list

                  GET /v1beta1/{parent}/sandboxEnvironmentSnapshots

                  Lists SandboxEnvironmentSnapshots in a given reasoning engine.

        REST Resource: v1beta1.projects.locations.reasoningEngines.sandboxEnvironmentTemplates

                Methods

                  create

                  POST /v1beta1/{parent}/sandboxEnvironmentTemplates

                  Creates a SandboxEnvironmentTemplate in a given reasoning engine.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes the specific SandboxEnvironmentTemplate.

                  get

                  GET /v1beta1/{name}

                  Gets details of the specific SandboxEnvironmentTemplate.

                  list

                  GET /v1beta1/{parent}/sandboxEnvironmentTemplates

                  Lists SandboxEnvironmentTemplates in a given reasoning engine.

        REST Resource: v1beta1.projects.locations.reasoningEngines.sandboxEnvironments

                Methods

                  authorizeAccess

                  POST /v1beta1/{name}:authorizeAccess

                  Checks whether the caller is authorized to access the sandbox environment.

                  bidiExecute

                  POST /v1beta1/{name}:bidiExecute

                  Executes using a sandbox environment with bidirectional streaming.

                  create

                  POST /v1beta1/{parent}/sandboxEnvironments

                  Creates a SandboxEnvironment in a given reasoning engine.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes the specific SandboxEnvironment.

                  execute

                  POST /v1beta1/{name}:execute

                  Executes using a sandbox environment.

                  get

                  GET /v1beta1/{name}

                  Gets details of the specific SandboxEnvironment.

                  list

                  GET /v1beta1/{parent}/sandboxEnvironments

                  Lists SandboxEnvironments in a given reasoning engine.

                  pause

                  POST /v1beta1/{name}:pause

                  Pauses the specific SandboxEnvironment.

                  resume

                  POST /v1beta1/{name}:resume

                  Resumes the specific SandboxEnvironment.

                  snapshot

                  POST /v1beta1/{name}:snapshot

                  Snapshots the specific SandboxEnvironment resource and creates a SandboxEnvironmentSnapshot resource.

        REST Resource: v1beta1.projects.locations.reasoningEngines.sessions

                Methods

                  appendEvent

                  POST /v1beta1/{name}:appendEvent

                  Appends an event to a given session.

                  create

                  POST /v1beta1/{parent}/sessions

                  Creates a new Session.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes details of the specific Session.

                  get

                  GET /v1beta1/{name}

                  Gets details of the specific Session.

                  list

                  GET /v1beta1/{parent}/sessions

                  Lists Sessions in a given reasoning engine.

                  patch

                  PATCH /v1beta1/{session.name}

                  Updates the specific Session.

        REST Resource: v1beta1.projects.locations.reasoningEngines.sessions.events

                Methods

                  list

                  GET /v1beta1/{parent}/events

                  Lists Events in a given session.

        REST Resource: v1beta1.projects.locations.schedules

                Methods

                  create

                  POST /v1beta1/{parent}/schedules

                  Creates a Schedule.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a Schedule.

                  get

                  GET /v1beta1/{name}

                  Gets a Schedule.

                  list

                  GET /v1beta1/{parent}/schedules

                  Lists Schedules in a Location.

                  patch

                  PATCH /v1beta1/{schedule.name}

                  Updates an active or paused Schedule.

                  pause

                  POST /v1beta1/{name}:pause

                  Pauses a Schedule.

                  resume

                  POST /v1beta1/{name}:resume

                  Resumes a paused Schedule to start scheduling new runs.

        REST Resource: v1beta1.projects.locations.semanticGovernancePolicies

                Methods

                  create

                  POST /v1beta1/{parent}/semanticGovernancePolicies

                  Creates a SemanticGovernancePolicy.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a SemanticGovernancePolicy.

                  get

                  GET /v1beta1/{name}

                  Gets a SemanticGovernancePolicy.

                  list

                  GET /v1beta1/{parent}/semanticGovernancePolicies

                  Lists SemanticGovernancePolicies in a given location.

                  patch

                  PATCH /v1beta1/{semanticGovernancePolicy.name}

                  Updates a SemanticGovernancePolicy.

        REST Resource: v1beta1.projects.locations.semanticGovernancePolicyEngine

                Methods

                  deprovision

                  POST /v1beta1/{name}:deprovision

                  Deprovisions the SemanticGovernancePolicyEngine, tearing down the associated tenant project, GKE cluster, and PSC service attachments.

        REST Resource: v1beta1.projects.locations.skills

                Methods

                  create

                  POST /v1beta1/{parent}/skills

                  Create a Skill.

                  delete

                  DELETE /v1beta1/{name}

                  Delete a Skill.

                  get

                  GET /v1beta1/{name}

                  Get a Skill.

                  list

                  GET /v1beta1/{parent}/skills

                  List Skills.

                  patch

                  PATCH /v1beta1/{skill.name}

                  Update a Skill.

                  retrieve

                  GET /v1beta1/{parent}/skills:retrieve

                  Retrieves skills.

        REST Resource: v1beta1.projects.locations.skills.revisions

                Methods

                  get

                  GET /v1beta1/{name}

                  Get a Skill Revision.

                  list

                  GET /v1beta1/{parent}/revisions

                  List Skill Revisions for a Skill.

        REST Resource: v1beta1.projects.locations.specialistPools

                Methods

                  create

                  POST /v1beta1/{parent}/specialistPools

                  Creates a SpecialistPool.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a SpecialistPool as well as all Specialists in the pool.

                  get

                  GET /v1beta1/{name}

                  Gets a SpecialistPool.

                  list

                  GET /v1beta1/{parent}/specialistPools

                  Lists SpecialistPools in a Location.

                  patch

                  PATCH /v1beta1/{specialistPool.name}

                  Updates a SpecialistPool.

        REST Resource: v1beta1.projects.locations.studies

                Methods

                  create

                  POST /v1beta1/{parent}/studies

                  Creates a Study.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a Study.

                  get

                  GET /v1beta1/{name}

                  Gets a Study by name.

                  list

                  GET /v1beta1/{parent}/studies

                  Lists all the studies in a region for an associated project.

                  lookup

                  POST /v1beta1/{parent}/studies:lookup

                  Looks a study up using the user-defined display_name field instead of the fully qualified resource name.

        REST Resource: v1beta1.projects.locations.studies.trials

                Methods

                  addTrialMeasurement

                  POST /v1beta1/{trialName}:addTrialMeasurement

                  Adds a measurement of the objective metrics to a Trial.

                  checkTrialEarlyStoppingState

                  POST /v1beta1/{trialName}:checkTrialEarlyStoppingState

                  Checks whether a Trial should stop or not.

                  complete

                  POST /v1beta1/{name}:complete

                  Marks a Trial as complete.

                  create

                  POST /v1beta1/{parent}/trials

                  Adds a user provided Trial to a Study.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a Trial.

                  get

                  GET /v1beta1/{name}

                  Gets a Trial.

                  list

                  GET /v1beta1/{parent}/trials

                  Lists the Trials associated with a Study.

                  listOptimalTrials

                  POST /v1beta1/{parent}/trials:listOptimalTrials

                  Lists the pareto-optimal Trials for multi-objective Study or the optimal Trials for single-objective Study.

                  stop

                  POST /v1beta1/{name}:stop

                  Stops a Trial.

                  suggest

                  POST /v1beta1/{parent}/trials:suggest

                  Adds one or more Trials to a Study, with parameter values suggested by Agent Platform Vizier.

        REST Resource: v1beta1.projects.locations.tensorboards

                Methods

                  batchRead

                  GET /v1beta1/{tensorboard}:batchRead

                  Reads multiple TensorboardTimeSeries' data.

                  create

                  POST /v1beta1/{parent}/tensorboards

                  Creates a Tensorboard.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a Tensorboard.

                  get

                  GET /v1beta1/{name}

                  Gets a Tensorboard.

                  list

                  GET /v1beta1/{parent}/tensorboards

                  Lists Tensorboards in a Location.

                  patch

                  PATCH /v1beta1/{tensorboard.name}

                  Updates a Tensorboard.

                  readSize

                  GET /v1beta1/{tensorboard}:readSize

                  Returns the storage size for a given TensorBoard instance.

                  readUsage

                  GET /v1beta1/{tensorboard}:readUsage

                  Returns a list of monthly active users for a given TensorBoard instance.

        REST Resource: v1beta1.projects.locations.tensorboards.experiments

                Methods

                  batchCreate

                  POST /v1beta1/{parent}:batchCreate

                  Batch create TensorboardTimeSeries that belong to a TensorboardExperiment.

                  create

                  POST /v1beta1/{parent}/experiments

                  Creates a TensorboardExperiment.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a TensorboardExperiment.

                  get

                  GET /v1beta1/{name}

                  Gets a TensorboardExperiment.

                  list

                  GET /v1beta1/{parent}/experiments

                  Lists TensorboardExperiments in a Location.

                  patch

                  PATCH /v1beta1/{tensorboardExperiment.name}

                  Updates a TensorboardExperiment.

                  write

                  POST /v1beta1/{tensorboardExperiment}:write

                  Write time series data points of multiple TensorboardTimeSeries in multiple TensorboardRun's.

        REST Resource: v1beta1.projects.locations.tensorboards.experiments.runs

                Methods

                  batchCreate

                  POST /v1beta1/{parent}/runs:batchCreate

                  Batch create TensorboardRuns.

                  create

                  POST /v1beta1/{parent}/runs

                  Creates a TensorboardRun.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a TensorboardRun.

                  get

                  GET /v1beta1/{name}

                  Gets a TensorboardRun.

                  list

                  GET /v1beta1/{parent}/runs

                  Lists TensorboardRuns in a Location.

                  patch

                  PATCH /v1beta1/{tensorboardRun.name}

                  Updates a TensorboardRun.

                  write

                  POST /v1beta1/{tensorboardRun}:write

                  Write time series data points into multiple TensorboardTimeSeries under a TensorboardRun.

        REST Resource: v1beta1.projects.locations.tensorboards.experiments.runs.timeSeries

                Methods

                  create

                  POST /v1beta1/{parent}/timeSeries

                  Creates a TensorboardTimeSeries.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a TensorboardTimeSeries.

                  exportTensorboardTimeSeries

                  POST /v1beta1/{tensorboardTimeSeries}:exportTensorboardTimeSeries

                  Exports a TensorboardTimeSeries' data.

                  get

                  GET /v1beta1/{name}

                  Gets a TensorboardTimeSeries.

                  list

                  GET /v1beta1/{parent}/timeSeries

                  Lists TensorboardTimeSeries in a Location.

                  patch

                  PATCH /v1beta1/{tensorboardTimeSeries.name}

                  Updates a TensorboardTimeSeries.

                  read

                  GET /v1beta1/{tensorboardTimeSeries}:read

                  Reads a TensorboardTimeSeries' data.

                  readBlobData

                  GET /v1beta1/{timeSeries}:readBlobData

                  Gets bytes of TensorboardBlobs.

        REST Resource: v1beta1.projects.locations.trainingPipelines

                Methods

                  cancel

                  POST /v1beta1/{name}:cancel

                  Cancels a TrainingPipeline.

                  create

                  POST /v1beta1/{parent}/trainingPipelines

                  Creates a TrainingPipeline.

                  delete

                  DELETE /v1beta1/{name}

                  Deletes a TrainingPipeline.

                  get

                  GET /v1beta1/{name}

                  Gets a TrainingPipeline.

                  list

                  GET /v1beta1/{parent}/trainingPipelines

                  Lists TrainingPipelines in a Location.

        REST Resource: v1beta1.projects.locations.tuningJobs

                Methods

                  cancel

                  POST /v1beta1/{name}:cancel

                  Cancels a tuning job.

                  create

                  POST /v1beta1/{parent}/tuningJobs

                  Creates a tuning job.

                  get

                  GET /v1beta1/{name}

                  Gets a tuning job.

                  list

                  GET /v1beta1/{parent}/tuningJobs

                  Lists tuning jobs in a location.

                  rebaseTunedModel

                  POST /v1beta1/{parent}/tuningJobs:rebaseTunedModel

                  Rebase a tuned model.

                  validateReinforcementTuningReward

                  POST /v1beta1/{parent}/tuningJobs:validateReinforcementTuningReward

                  Validates a reward on a given example.

        REST Resource: v1beta1.projects.modelGardenEula

                Methods

                  accept

                  POST /v1beta1/{parent}/modelGardenEula:accept

                  Accepts the EULA acceptance status of a publisher model.

                  check

                  POST /v1beta1/{parent}/modelGardenEula:check

                  Checks the EULA acceptance status of a publisher model.

        REST Resource: v1beta1.projects.publishers.models

                Methods

                  enableModel

                  POST /v1beta1/{parent}/{name}:enableModel

                  Enables model for the project if prerequisites are met (e.g.

        REST Resource: v1beta1.publishers.models

                Methods

                  get

                  GET /v1beta1/{name}

                  Gets a Model Garden publisher model.

                  list

                  GET /v1beta1/{parent}/models

                  Lists publisher models in Model Garden.

    Send feedback

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2026-09-02 UTC.

    Need to tell us more?

      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-09-02 UTC."],[],[]]
