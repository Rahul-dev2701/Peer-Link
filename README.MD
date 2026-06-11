# Peer-to-Peer Network Simulation

A simulation of a P2P network built in Python using TCP sockets.
Implements seed nodes, peer discovery, gossip protocol, and liveness detection.

## Project structure

- `log.py` — thread-safe logging utility
- `seeds.py` — seed node (network registry)
- `peers.py` — peer node (connects, gossips, pings)
- `main.py` — launches seed nodes from config
- `new_peer.py` — launches a single peer node
- `config.txt` — list of seed node addresses (ip:port)
- `OUTPUT.txt` — generated log file (git-ignored)

## How to run

_(Instructions will be added once all components are complete.)_