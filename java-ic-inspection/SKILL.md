---
name: java-ic-inspection
description: Expertise in developing Java-based systems for automotive IC chip inspection focusing on CAN, LIN, and CAN FD protocols. Use this skill when the user wants to build tools for monitoring, simulating, or inspecting automotive bus communications
---

# Java Automotive IC Inspection (CAN/LIN/CAN FD)

Expertise in developing Java-based systems for automotive IC chip inspection focusing on CAN, LIN, and CAN FD protocols. Use this skill when the user wants to build tools for monitoring, simulating, or inspecting automotive bus communications.

## Core Responsibilities
1. **Bus Protocol Implementation**: Deep knowledge of CAN 2.0, CAN FD (Flexible Data-rate), and LIN protocols.
2. **Frame Handling**: Designing data structures for Frames (ID, DLC, Payload, Timestamps) and handling CAN FD specific features like BRS (Bit Rate Switch) and ESI (Error State Indicator).
3. **Hardware Interfacing**: Using Java Native Access (JNA) or specific wrappers for PCAN, Kvaser, or Vector hardware.
4. **Signal Extraction (DBC/LDF)**: Logic for parsing raw bus data into human-readable signals based on database definitions (DBC for CAN, LDF for LIN).
5. **Real-time Monitoring**: Handling high-bus-load scenarios using efficient buffering and thread-safe queues.

## Protocol Specifics
- **CAN FD**: Support for up to 64 bytes of payload and dual bitrates.
- **LIN**: Handling Master/Slave architecture, Scheduling, and Checksum calculations.
- **Error Analysis**: Detecting Error Frames, Bus-off states, and protocol violations.

## Architecture Patterns
- **Protocol Provider Interface**: A generic interface to allow switching between CAN, CAN FD, and LIN providers.
- **Dispatcher/Subscriber**: Efficiently routing incoming frames to specific signal parsers based on Message ID.
- **Circular Buffers**: For low-latency data ingestion.

## Code Standards
- Use `double` or `BigDecimal` for precision measurements.
- Implement robust error handling for hardware disconnects.
- Provide unit tests for DSP logic using mock signal data.
