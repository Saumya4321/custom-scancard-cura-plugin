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
<img width="734" height="675" alt="image" src="https://github.com/user-attachments/assets/84b89942-66b8-4002-b528-409654ebade6" />

### Thread - safe cancellation flow
<img width="610" height="443" alt="image" src="https://github.com/user-attachments/assets/0c022347-bf34-472a-bfd3-96dc7a9b398c" />

<em>NOTE: Cleanup happens only after the thread has fully exited, preventing race conditions and crashes</em>
