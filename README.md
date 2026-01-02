# Cura Scan Card Plugin

Hardware-Agnostic Toolpath Processing and UDP Streaming Pipeline

## Overview

This repository contains a production Cura plugin and backend pipeline designed to convert sliced geometry into hardware-ready scan vectors and stream them to a custom laser scan card over UDP.

Although Cura is used as the frontend slicer, the core processing pipeline is fully decoupled from Cura and can be reused with other CAD/CAM tools or custom frontends.

Cura acts only as a framework-level UI and mesh provider; all geometry processing, path planning, packetization, and hardware communication are implemented as independent, reusable modules.

## Key Features

- Cura plugin for extracting sliced geometry / G-code
  - Designed for additive manufacturing / laser scanning systems

- Backend pipeline for:

    + Geometry normalization

    + Path interpolation and planning

    + Galvo coordinate transformation

    + Hardware-specific packetization

    + Real-time UDP streaming to a custom scan card

- Clean separation between UI, domain logic, and hardware interfaces i.e. Core logic has no dependency on Cura
and hardware communication is abstracted behind interfaces . The same pipeline can be reused for:

  + Different slicers

  + Different scan cards
 
## Status

This project is under active development and is used as part of a real manufacturing control pipeline.

## Author 
[Saumya B](https://www.linkedin.com/in/saumya-b-) ,
Project Assistant, IISc

