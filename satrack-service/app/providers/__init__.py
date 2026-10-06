from app.providers.simulator import SimulatorProvider


def get_provider(settings):
    if settings.provider == "simulator":
        return SimulatorProvider()
    if settings.provider == "satrack":
        from app.providers.satrack import SatrackProvider
        return SatrackProvider(settings)
    raise ValueError("PROVIDER debe ser satrack o simulator")
