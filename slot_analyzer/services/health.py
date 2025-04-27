class HealthService:
    def check_health(self):
        return {
            "status": "healthy",
            "components": {}
        }

health_service = HealthService()