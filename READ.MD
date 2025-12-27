🚦 Traffic Signal Management System

A scalable, extensible simulation of a smart traffic signal controller that manages traffic at road intersections using clean architecture principles, design patterns, and real-world constraints.

⸻

🧠 Intuition

In real life, a traffic intersection behaves as a single coordinated system:
	•	It controls multiple traffic lights
	•	Only one direction can move at a time
	•	Traffic density changes constantly
	•	Emergency vehicles require immediate priority

This project models that real-world behavior in software using well-structured object-oriented design.

⸻

🎯 Objectives
	•	Enforce safety: never allow conflicting green signals
	•	Support automatic cycling: NORTH → EAST → SOUTH → WEST
	•	Provide emergency override with safe recovery
	•	Adapt signal timing based on traffic density
	•	Maintain a clean, testable architecture

⸻

🧱 Architecture Overview
Controller
   ↓
Services (business rules)
   ↓
Repositories (storage)
   ↓
Domain Entities

This separation ensures:
	•	high maintainability
	•	easy testing
	•	low coupling
	•	future scalability

⸻

🧩 Core Domain Entities

🏙️ Intersection

Represents a real intersection and acts as the aggregate root.
	•	Owns 4 TrafficSignals
	•	Maintains cycle order
	•	Remembers current phase
	•	Coordinates all activity within the intersection

🚦 TrafficSignal

Represents one traffic light.
	•	Knows its direction
	•	Maintains its timing configuration
	•	Uses the State Pattern for behavior

🎛 SignalTiming

Encapsulates configurable timing parameters:
	•	green
	•	yellow
	•	red

⸻

🔄 State Design Pattern

Traffic signal behavior is modeled using:

SignalState (interface)
   ↑
RedState → GreenState → YellowState → RedState

Each state:
	•	controls its own behavior
	•	determines the next transition
	•	eliminates conditional logic

This makes the system extensible and robust.

⸻

🧯 Safety Enforcement

All safety rules are centralized in SignalService.

Before any signal becomes GREEN:
	1.	All signals are forced to RED
	2.	The requested signal becomes GREEN

This guarantees no conflicting greens.

⸻

🚗 Dynamic Traffic Optimization

The system tracks vehicle count per direction and adjusts green timing:

Traffic Volume     Behavior
High               Increase green duration
Low                Reduce green duration
Normal             Keep default timing

This ensures optimal throughput under changing conditions.

⸻

🚨 Emergency Handling

When an emergency request arrives:
	1.	The cycle is paused
	2.	All signals turn RED
	3.	Emergency direction turns GREEN
	4.	Emergency clears
	5.	Cycle resumes from same phase

This provides both safety and fairness.

⸻

🔁 Cycle Control Logic

CycleService acts as the brain of the system.

On each iteration:
	1.	Check emergency
	2.	Compute dynamic timing
	3.	Activate safe green
	4.	Transition through states
	5.	Advance cycle pointer

⸻

🧪 Clean Architecture Layers

🎮 Controller

Coordinates application actions only.
Never touches repositories.

⚙️ Services

Contain all business rules:
	•	safety
	•	timing
	•	emergency handling
	•	optimization

🗄 Repositories

Handle all data storage and retrieval.
Can be replaced with databases or distributed stores.

⸻

🧬 Extensibility

This architecture supports:
	•	multiple intersections
	•	centralized city traffic control
