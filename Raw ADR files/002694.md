# Device Gateway Wired Communication with On-Premise Server "MonitorMe"

## Context
The on-premise server "MonitorMe" serves as a vital component in the hospital's data management infrastructure. 
It's responsible for receiving, storing, and updating patient medical data from various sources, including the devices mentioned earlier. 
Given the critical nature of this data and the need for rapid access, 
ensuring a robust and reliable communication method between the devices and the server is paramount.

## Status
Proposed

## Decision
The decision is to implement a wired communication protocol between the Device Gateway and the on-premise server "MonitorMe."
Reasons for this choice are:
   * Reliability: Wired connections generally offer better reliability and consistency compared to wireless alternatives, reducing the risk of data loss or transmission errors.
   * Security: Wired communication is inherently more secure as it's not subject to the same vulnerabilities as wireless transmissions, such as interception or interference.
   * Bandwidth: Wired connections typically offer higher bandwidth, allowing for faster data transfer, essential for real-time patient monitoring.
   * Stability: Wired connections are less prone to environmental factors that can affect wireless signals, ensuring a stable and consistent connection.

## Consequences
Using a wired communication protocol brings plenty of pros and also some cons, as we minimize the risk of data corruption and loss, increasing security due to physical wires, 
and also being a fast and reliable way to access the on-premise server data quickly which enbles faster decision making. The infrastructure setup cost is to be mentioned, as
implementing this would require additional investment in cabling, switches and other related equipment, as well as installation and maintenance.

## Options

  * Wireless Redundancy: One pretty obvious option would be implementing a backup wireless communication channel alongside the primary wired connection to provide redundancy and ensure continuous data transmission in case of wired network failures. This redundancy can enhance reliability without sacrificing the benefits of wired communication.
  * Hybrid Communication: We could explore the possibility of utilizing a hybrid communication approach, where critical data is transmitted via wired connections for reliability and security, while non-critical or supplementary data is transmitted wirelessly to enhance flexibility and scalability.
  * Fiber Optic Communication: Depending on available budget, we could consider upgrading the wired communication infrastructure to use fiber optic cables instead of traditional copper cables. Fiber optic cables offer higher bandwidth, longer transmission distances, and immunity to electromagnetic interference, making them ideal for high-speed and reliable data transfer.
  * Cloud-Based Data Storage: There is also the option of migrating data storage and management to a cloud-based platform instead of relying solely on the on-premise server "MonitorMe." Cloud-based solutions offer scalability, accessibility, and built-in redundancy, potentially reducing infrastructure costs and management overhead in the long term.

## Usefull links 
- [Infrastructure page](https://github.com/ArchitectsEvolutionZone/MonitorMe/blob/main/2.ArchitectureVisualization/Infrastructure.md)
