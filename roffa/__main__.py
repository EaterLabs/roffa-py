from .roffa import RoffaConfig, Roffa

roffa = Roffa()

roffa.load_config({
    "districts": {
        "http": {
            "containers": {
                "web": {
                    "image": "d.xr.to/nginx",
                    "amount": 2,
                }
            }
        }
    }
})

roffa.collect_state()
roffa.collect_actions()
roffa.run_actions()
