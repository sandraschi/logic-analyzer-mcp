# Per-repo fleet start config for logic-analyzer-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'logic-analyzer-mcp'
    BackendPort  = 10985
    FrontendPort = 10989
    HealthPath   = '/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'logic_analyzer_mcp.server:app'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '10985' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
