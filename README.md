# roffa

There is a dock there! so the name makes sense!!

---

roffa is (yet another) docker orchestration tool, focused on simplicity and usability.

# Design

roffa's design is heavily inspired by how puppet works, there are 2 stages, a state collection stage and a action stage.

First roffa will load the desired state into memory, then it will start querying Docker about the current state of the containers.
with those 2 states it'll create a task list, which will bring the current state to the desired state, this is the state collection stage.
This task list is then executed, this is the action stage.

roffa also needed a hip name for clusters, so it uses the name 'districts', quite similar to what pods are in kubernetes.
these districts are just collection of containers that are inter-connected.