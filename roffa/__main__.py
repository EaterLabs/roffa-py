from .roffa import RoffaConfig

print(RoffaConfig.from_config({
    "districts": {
        "http": {
            "containers": {
                "web": {
                    "image": ""
                }
            }
        }
    }
}))