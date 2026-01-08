## v2 - Multithreaded Print Execution

This branch refactors the print pipeline to run asynchronously using Qt multithreading, ensuring the Cura UI remains responsive during long print jobs.

### Summary of Changes

- Moved all heavy print operations (G-code processing, layer parsing, payload generation, UDP streaming) into a dedicated ```PrintWorker``` running in a ```QThread```.

- Implemented signal–slot based communication for progress updates, completion, errors, and cancellation.

- Added graceful cancellation support with cooperative stop checks at every critical stage, including mid-UDP transmission.

- Updated the UDP sender to support real-time interruption via a ```stop_check``` callback.

- Introduced robust thread and signal cleanup to prevent UI freezes, crashes, and dangling threads.

### Outcome

- Non-blocking UI during printing

- Safe and responsive print cancellation

- Clean separation between UI control and print execution logic

### High-Level Architecture Diagram

<img width="464" height="911" alt="image" align="center" src="https://github.com/user-attachments/assets/586f47c5-46e0-43b5-baaf-892c6050b9de" />
