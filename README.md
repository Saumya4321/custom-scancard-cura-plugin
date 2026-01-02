# Cura Scan Card Plugin

Hardware-Agnostic Toolpath Processing and UDP Streaming Pipeline

## Overview

This repository contains a production Cura plugin and backend pipeline designed to convert sliced geometry into hardware-ready scan vectors and stream them to a custom laser scan card over UDP.

Although Cura is used as the frontend slicer, the core processing pipeline is fully decoupled from Cura and can be reused with other CAD/CAM tools or custom frontends.

Cura acts only as a framework-level UI and mesh provider; all geometry processing, path planning, packetization, and hardware communication are implemented as independent, reusable modules.
