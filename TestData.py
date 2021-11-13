
# Username to use when constructing new comments
Username = "CountTheComments"

# File to store active jobs in
ActiveJobFile = "activeJobsTest.json"

# Possible comment authors
Authors = ["authorA", "authorB"]

# Possible comments to count, these are assuming the relevant terms are 1+ of
# rem ram felix felis emilia emt
CommentsTermPairs = [
    ("Ram", ["ram"]),
    ("RAM", ["ram"]),
    ("rem", ["rem"]),
    ("I choose Felix!", ["felix"]),
    ("felis easily", ["felis"]),
    ("Emilia tan", ["emilia"]),
    ("EMT", ["emt"]),
    ("Ram Rem", ["ram", "rem"]),
    ("Rem Ram", ["rem", "ram"]),
    ("Emilia Maji Tenshi Emilia Ram Rem", ["emilia", "ram", "rem"]),
    ("Rem Rem Rem Rem Rem Ram Rem Rem Rem", ["rem", "ram"]),
    ("Ram then rem in that order", ["ram", "rem"]),
    ("Fr though like this is actually me hiding in the test data, Ram is best girl", ["ram"]),
    ("It'd have to be Felix i think", ["felix"]),
    ("I don't remember :(", []),
    ("Emili Ram", ["ram"]),
    ("E.M.T.", []),
    ("E.M.T. number 1, Rem number 2!", ["rem"]),
    ("Toss up between emilia and rem", ["emilia", "rem"])
]

Comments = [i[0] for i in CommentsTermPairs]

# Valid summons with terms to be parsed
SummonCommentPairs = [
    ("u/CountTheComments Rem Ram Rem Ram Rem Ram Rem Ram", [["rem"], ["ram"]]),
    ("u/CountTheComments Rem/Ram Ram/Felix Rem/Ram/Ram/Rem", [["rem", "ram"], ["ram", "felix"]]),
    ("u/CountTheComments Rem/Ram/Rem REM/REM/RAM rem/ram/ram/ram rem/rem/ram/ram", [["rem", "ram"]]),
    ("u/CountTheComments Rem/Ram Ram/Rem", [["rem", "ram"], ["ram", "rem"]]),
    ("u/CountTheComments Rem/Rem", [["rem"]]),
    ("u/CountTheComments rem/REM", [["rem"]]),
    ("u/CountTheComments Rem/Rem/Ram", [["rem", "ram"]]),
    ("u/CountTheComments Ram/Rem/Ram", [["ram", "rem"]]),
    ("u/CountTheComments Rem/Ram Emilia Ram/Rem", [["rem", "ram"], ["emilia"], ["ram", "rem"]]),
    ("u/CountTheComments Rem/Ram Rem/Felix", [["rem", "ram"], ["rem", "felix"]]),
    ("u/CountTheComments Rem Ram Felix/Felis Emilia/EMT", [["rem"], ["ram"], ["felix", "felis"], ["emilia", "emt"]]),
    (" u/CountTheComments Rem Ram Felix", [["rem"], ["ram"], ["felix"]]),
    ("          u/CountTheComments Rem Ram Felix", [["rem"], ["ram"], ["felix"]]),
    ("         /u/CountTheComments Rem Ram Felix", [["rem"], ["ram"], ["felix"]]),
    ("u/countthecomments rem ram felix", [["rem"], ["ram"], ["felix"]]),
    ("u/COUNTTHECOMMENTS rem Ram", [["rem"], ["ram"]]),
    ("/u/COuntTheComments Rem Ram Felix", [["rem"], ["ram"], ["felix"]]),
    ("/u/COuntTheComments Rem                    Ram   Felix", [["rem"], ["ram"], ["felix"]]),
    ("u/CountTheComments Rem Rem", [["rem"]]),
    ("u/CountTheComments Rem/Ram Rem/Emilia Emilia/Rem", [["rem", "ram"], ["rem", "emilia"], ["emilia", "rem"]]),
    ("u/CountTheComments REM/Ram rem/Emilia", [["rem", "ram"], ["rem", "emilia"]]),
    ("u/CountTheComments REM/Ram Emilia Ram", [["rem", "ram"], ["emilia"], ["ram"]]),
    ("Summoning u/CountTheComments Rem Ram", [["rem"], ["ram"]]),
    ("         /    u/CountTheComments Rem Ram Felix", [["rem"], ["ram"], ["felix"]]), 
    ("!!!.? u/CountTheComments Rem Ram Felix", [["rem"], ["ram"], ["felix"]])
]

SummonComments = [i[0] for i in SummonCommentPairs]


# Valid mentions, but incorrectly formatted terms
InvalidSummonComments = [
    "u/CountTheComments",
    "u/CountTheComments ... Ram Felix",
    "u/CountTheComments ...Ram Felix",
    "/u/CountTheComments",
    "test and then u/Countthecomments",
    "test and then /u/CountTheComments",
    "/u/CountTheComments Rem//Ram",
    "/u/CountTheComments Rem/Ram/",
    "/u/CountTheComments /Rem",
    "/u/CountTheComments /",
    "/u/CountTheComments         !",
    "u/CountTheComments Rem Felix / Felis Emilia /EMT",
    "u/CountTHeCOmments rem felix ff/ felis",
    "u/CountTHeCOmments rem felix ff /felis",
    "u/CountTheComments Rem Ram Felix/Felis Emilia/EMT/E.M.T/Emilia Maji Tenshi",
    "Can we get u/CountTheComments Rem Ram in here?",
    "/u/CountTHeComments term1  term2 term3. term4",
    "/u/CountTHeComments term1  term2 term3.term4",
    "/u/CountTHeComments term1  term2 term3 .term4",
    "/u/CountTHeComments term1  term2 term3 . term4",
    "/u/CountTHeComments term1  term2 term3.",
    "/u/CountTHeComments term1  term2 term3 term4.."
]


# Invalid mentions (in inbox due to comment replies)
ReplyComments = [
    "u/CountTheComments... Ram Felix",
    "u/CounteTheComments&one&two",
    "test/u/CountTheComments rem ram",
    "u/countthecommentsrem ram",
    "Uhhhhu/CountTheComments Rem Ram",
    "CountTHeComments marker1 marker2"
    "!/u/CountTheComments Rem Ram Felix",
    "!u/CountTheComments Rem Ram Felix",
    "/CountTheComments Rem Ram Felix",
    "CountTheComments Rem Ram Felix",
]

PMs = [
    "Hi /u/CountTheComments",
    "/u/CountTheComments pmTerm1 pmTerm2",
    "This is feedback for the bot"
]

# All comments that will arrive in inbox
InboxComments = SummonComments + InvalidSummonComments + ReplyComments + PMs