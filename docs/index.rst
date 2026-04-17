The Lockport Arcade
===================

The Lockport Arcade is a student-built arcade machine. It is a custom wooden
cabinet with a joystick and buttons, running a library of original video games,
with a soundtrack of original sound effects—designed and built by students 
at Lockport High School in collaboration with their teachers and 
researchers at the University at Buffalo.

The Lockport Arcade was built by students across four different disciplines:

- **Introductory CS students** taking the `Making With Code games unit
  <https://lockport.makingwithcode.org/courses/mwc1/>`_ wrote the games.
  For many of them, this was one of their first experiences with programming.
  Their games run on the arcade.

- **Advanced CS students** designed the console software itself:
  the arcade menu, the high score system, and the infrastructure that ties
  all the games together. This documentation is for the people who install
  and maintain that software, and for future students who want to write
  games or sounds for it.

- **Engineering students** designed and fabricated the physical cabinet —
  the wooden enclosure, the joystick and button panel, and the hardware
  that connects it all. They turned a software project into something you
  can walk up to and play.

- **Music students** composed the sound effects: the theme song that plays
  while you wait, the sounds that fire when a game starts, and the effects
  that respond to every jump, explosion, and collected point inside each
  game.

The ideas behind the project
-----------------------------

The Lockport Arcade is part of **Making With Code** (MWC), a Constructionist
introductory computer science curriculum developed at the University at Buffalo
in collaboration with Lockport High School. Constructionism, a learning theory
developed by Seymour Papert, holds that people learn most powerfully when they
are making things that other people will use and care about — not just solving
exercises for a grade. Making With Code is designed around this idea: every
unit ends with a real project, and the games unit ends with games that run on
this arcade (Proctor et al., 2020).

One of the design principles behind the software tools used in Making With Code
is what the course's designers call **permeable media** (Proctor et al., 2025).
A permeable medium is a tool designed to welcome beginners in — keeping things
simple enough to get started quickly — while also supporting deeper engagement
as learners grow. The ``retro`` library used to write arcade games is designed
this way: a beginner can make a working game with just a few lines of Python,
but the same library supports arbitrarily complex game logic as students develop
their skills. The arcade console itself is designed along similar lines: intro
students can write a game without knowing anything about how the console works,
while advanced students can read and modify the console's source code directly.

The interdisciplinary structure of the project is itself a Constructionist
design choice. When introductory CS students know their games will be played on
a real arcade cabinet with real sounds, it changes what the project means to
them—and to the engineering and music students whose work makes that possible.
When student computer science projects are accessible to the broader student body, 
it helps more students become interested in computing. 


How to use these docs
---------------------

These docs are organized by role. Find the guide that matches what you're
doing:

.. toctree::
   :maxdepth: 2
   :caption: Contents

   console_manager
   game_developer
   sound_designer

References
----------

Proctor, C., Han, J., Wolf, J., Ng, K., & Blikstein, P. (2020). Recovering
constructionism in computer science: Design of a ninth-grade introductory
computer science course. *Constructionism 2020 Papers*, 473–482.

Proctor, C., Paljor, Y., & Bhatt, V. (2025). Permeable media: A design
strategy for Constructionist software. *Constructionism Conference
Proceedings*, 8/2025, 239–248. https://doi.org/10.21240/constr/2025/51.X
