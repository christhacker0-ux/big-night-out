# Big Night Out: story bible

An original comedy point-and-click. Freshman Dex Dooley signs up for the campus round of the TV dating show
**Speed Daters Live**, hosted by **Roxy Vale**, and has to survive five rounds in one very long night.
Everything here is original: no names, characters, art or text from any other game.

Tone: warm, silly, PG-13 innuendo at most. Dex is a nervous, decent guy who wins people over by helping them.
Every woman Dex meets has her own problem; Dex solves it, and she gives him a **token** (a keepsake item he keeps).
Each act ends with a **round** hosted by Roxy that needs that act's tokens.

## Rules for every act
- Each woman's chain is 3 to 5 steps, and at least one item or fact from one chain solves another (chains cross).
- Every puzzle is solvable from what the player can see and read; Dex hints in his own lines when stuck.
- Characters remember progress: every talk node branches on flags so nobody repeats a finished request.
- Inventory carries over between acts. Puzzle items are taken when used; tokens are kept forever.
- The act's round, once won, runs `<<act N+1>>` and says where to go next (the campus map, Info kiosk, unlocks it).
- Each act's exit back to campus uses `<<go campus from_map>>`. Arriving from the map uses entry `from_campus`.

## Cast so far
- **Dex Dooley**: hero, room 214, turquoise hibiscus shirt, spiky orange hair.
- **Uncle Vic**: Dex's mentor, only in letters and phone calls. Advice: "Be the guy who shows up with what they need."
- **Roxy Vale**: host. Calls Dex "lover boy". Appears at each act's round.
- **Lacey Rae** (Act 1): country girl. Loves Hank Hollister. Token: cowboy hat.
- **Gil** (Act 1): sleepless neighbour in a bathrobe; snoring roommate.
- **Ivy** (Act 1): shy poet in the library. Poem: "Ode to the Quiet Kid in the Back Row". Token: bookmark with a pressed daisy.
- **Ms. Hush** (Act 1): head librarian. Founder statue: Augustus Plumworth.

## Acts
Each act has a verbal duel where Dex first learns the right comebacks from other characters, plus trading chains, disguises and distractions. Every character talks through a topic menu that changes as the story moves on. Docs/walkthrough/ has the exact solution per act.

| Act | Round | Rooms (id) | Women | Other cast |
|---|---|---|---|---|
| 1 Freshman | Talent Round, campus stage | dex_room, dorm_hallway, lounge, gil_room, campus, student_union, library, library_stacks | Lacey Rae, Ivy | Gil, Boomer, Doreen, Kyle, Percival Thorne, Ms. Hush, Roxy |
| 2 Greek Week | Quiz Round, Greek Row | greek_row, sorority_parlor, frat_house, frat_basement, fuse_box | Tess Calloway, Dolly Spark | Chad Thunderclap, Mother Whitlock, Moose, Dunk |
| 3 Lab Rats | Dare Round, the lab | science_hall, lab, rooftop, science_basement, faculty_lounge | Dr. Mina Volt, Sky Rivera | Professor Nibbles, Dot Pruitt, Professor Crumb, Mr. Bones |
| 4 Off Campus | Date Round, downtown | downtown, quickmart, rusty_anchor, starlite_diner, bijou_lobby | Bree Marlowe, Lou | Captain Gus, Sal, Mortimer, Admiral the parrot |
| 5 Uptown | Finals, the nightclub | uptown, cafe_snoot, art_gallery, nightclub, velour_backstage | Mimi, Jett Vex | Brutus, Pierre, Vivian Quill, Anton, Grizz, Mr. Pemberton |
| Finale | Live final and dance-off | tv_studio, tv_green_room, tv_control_booth | all of them, cheering | Roxy, rival Chet Studwell, Gloria Puff, Norma Fade, Uncle Vic on the phone |

### Act 2: Greek Week (Quiz Round)
- **Tess Calloway**, sorority president on the Greek Row porch: pearls, clipboard, runs everything. The frat stole the sorority
  mascot, a giant inflatable flamingo named **Fernanda**. Token: her sorority pin.
- **Chad Thunderclap**, frat president at the frat door: "Toga party. No toga, no entry."
- **Dolly Spark**, DJ at the Fuse Box bar: her amp keeps blowing the bar's only fuse. Token: a glow-stick bracelet.
- Chain: bedsheet from the sorority porch clothesline + safety pin = toga; wear it (give to Chad) to get in;
  pull a fuse from the frat's breaker box, lights out, grab Fernanda in the dark; Fernanda to Tess; fuse to Dolly.
- Quiz Round: Roxy asks questions whose answers Dex learned earlier (Lacey's singer, Ivy's poem, the flamingo's name,
  Dolly's favourite song...). Wrong answers can be retried.

### Act 3: Lab Rats (Dare Round)
- **Dr. Mina Volt**, grad student, wild hair, lab coat: her thesis hamster **Professor Nibbles** escaped into the vents.
  Token: her lucky safety goggles.
- **Sky Rivera**, activist with a dead megaphone on the rooftop: protesting hamster experiments. Token: a protest button.
- Chain crosses: catch Nibbles with a trap (seeds from the rooftop bird feeder + cardboard tube from lab recycling),
  get Mina to promise Nibbles a happy retirement as lab mascot, which also wins over Sky; Mina's spare batteries fix Sky's megaphone.
- Dare Round: Roxy issues dares; the right choices use what Dex learned and carries.

### Act 4: Off Campus (Date Round)
- **Bree Marlowe**, diner waitress and aspiring actress: needs headshots for an audition tomorrow. Token: her diner name tag.
- **Lou**, tough quickmart clerk who never smiles; stuck on the same crossword for a week. Token: the finished crossword.
- **Captain Gus**, regular at the Rusty Anchor, knows every sailor word; wants someone to play his song on the jukebox.
- Chain: Gus's crossword answer cheers up Lou, who gives Dex the disposable camera from behind the counter; photos for Bree.
- Date Round: plan a date on camera for Roxy, choosing place, gift and line that fit what he learned.

### Act 5: Uptown (Finals)
- **Mimi**, a street mime outside the gallery, "trapped" in an invisible box. Communicates only by gesture
  (Dex describes them). Token: her white glove.
- **Jett Vex**, punk rocker in the nightclub VIP area, bored of everything. Token: her guitar pick.
- **Brutus**, nightclub bouncer: list only. **Pierre**, snooty gallery curator.
- Chain: a crossing between the gallery (a "priceless" blank canvas, art supplies) and the club (getting on the list).
- Finals: Roxy asks Dex to make his case; choosing honesty over lines wins.

### Finale: Speed Daters Live
- Roxy hosts live from the tv_studio. Rival contestant **Chet Studwell** (perfect teeth, terrible person) is the last obstacle.
- Elimination: each token Dex collected becomes a callback; the women in the audience each help once.
- Dance-off with dialogue choices. Dex wins, Uncle Vic calls in, and the ending says THE END.
