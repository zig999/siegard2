# SIGARD Architecture Index

**Version:** 0.1 (Draft)

This document is the entry point for the SIGARD Architecture
Specification.

## Purpose

The documents are organized in a dependency order. Each document builds
upon the concepts introduced by the previous ones.

------------------------------------------------------------------------

# Architecture Core

  ---------------------------------------------------------------------------
        \# Document             Purpose              Depends On
  -------- -------------------- -------------------- ------------------------
         1 Core Architecture    Defines the vision,  \-
           Specification        principles and       
                                architectural        
                                foundations of       
                                SIGARD.              

         2 Workflow             Defines the          1
           Specification        lifecycle of every   
                                Change Request.      

         3 Knowledge Object     Defines the          1,2
           Specification        canonical model for  
                                Knowledge Objects    
                                (KOs).               

         4 Context Resolution   Defines how Context  1--3
           Specification        Packages are built   
                                deterministically.   

         5 Artifact             Defines every        1--4
           Specification        artifact exchanged   
                                throughout the       
                                workflow.            

         6 ADR Specification    Defines how          1--5
                                Architectural        
                                Decision Records are 
                                created and          
                                consumed.            

         7 Validation Model     Defines              1--6
           Specification        deterministic        
                                validation and       
                                evidence generation. 

         8 Knowledge Graph      Defines the          1--7
           Model Specification  Knowledge Graph and  
                                traversal rules.     

         9 Repository Layout &  Defines the          1--8
           Conventions          canonical repository 
           Specification        structure and        
                                conventions.         
  ---------------------------------------------------------------------------

------------------------------------------------------------------------

# Reading Order

The recommended reading sequence is:

1.  Core Architecture
2.  Workflow
3.  Knowledge Objects
4.  Context Resolution
5.  Artifacts
6.  ADRs
7.  Validation
8.  Knowledge Graph
9.  Repository Layout

------------------------------------------------------------------------

# Dependency Diagram

``` text
Core Architecture
        │
        ▼
Workflow
        │
        ▼
Knowledge Objects
        │
        ▼
Context Resolution
        │
        ▼
Artifact Model
        │
        ▼
ADR Model
        │
        ▼
Validation Model
        │
        ▼
Knowledge Graph
        │
        ▼
Repository Layout
```

------------------------------------------------------------------------

# Document Status

  Document             Status
  -------------------- --------
  Core Architecture    Draft
  Workflow             Draft
  Knowledge Objects    Draft
  Context Resolution   Draft
  Artifact Model       Draft
  ADR Model            Draft
  Validation Model     Draft
  Knowledge Graph      Draft
  Repository Layout    Draft

------------------------------------------------------------------------

# Next Phase

With these nine documents complete, the architectural foundation of
SIGARD is established.

The next documentation phase should focus on the operational model:

-   Command Model
-   Orchestrator Model
-   Worker Model
-   Hook Model
-   Skill Model
-   Execution Engine
