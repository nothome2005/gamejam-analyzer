class DistributionError(ValueError):
    pass

def validate_build_distribution(build_url: str, build_size_mb: float) -> bool:
    """
    Validates distribution parameters and 500 MB size limit (AC-F-004, BDD-SC-006).
    """
    if not build_url or not isinstance(build_url, str):
        raise DistributionError("URL дистрибуції обов'язковий")

    if build_size_mb > 500.0:
        raise DistributionError(f"Розмір білда ({build_size_mb} МБ) перевищує допустимий ліміт джему (500 МБ)")

    return True
