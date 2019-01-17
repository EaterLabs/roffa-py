# roffa

> **/ˌrɔff'a/** slang for Rotterdam, a city in South Holland, Netherlands.

There is a dock there! so the name makes sense!!

---

roffa is (yet another, maybe?) docker orchestration tool, focused on simplicity and usability.

# Design

roffa's design is heavily inspired by how puppet works, there are 3 stages, a state collection stage, action creation stage and an action execution stage.

1. State collection stage

    roffa will collect the current state from Docker
    
2. Action creation stage

    With the current state known, roffa creates an action list to get to the desired state
    
3. Action execution stage

    roffa executes the action list created in stage 2.

roffa also needed a hip name for a collection of interconnected containers, so it uses the name 'districts'.

# Features

* ehhh, not much atm.

## Planned

* HAProxy integration
    
    Instead of stopping a container and dropping all connections, the HAProxy backend is first set to drain, only when there are no connections left to the container the container will be stopped.

# Drawbacks

* Currently roffa only manages 1 docker daemon, so no real cluster management yet.
* roffa has no fancy web interface
* roffa doesn't use Go!

# When should I consider using this?

roffa is intended to be used in small Docker setups, that don't have a lot of complexity going on.

or if you just want to write 1 very simple config for your Docker setup and be done with it.

# Progress

- [x] Create containers
- [x] Connect networks to containers
- [ ] Create friendly CLI interface
- [ ] Create easy to deploy Docker container
- [ ] Create networks
- [ ] Create volumes
- [ ] Connect volumes to containers
- [ ] Configure containers in detail
- [ ] Configure HAProxy instance
- [ ] Auto-drain connections in HAProxy before removing container
- [ ] Multi-host support via _R A F T_ ([PySyncObject?](https://github.com/bakwc/PySyncObj)) and docker swarm 

