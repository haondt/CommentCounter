
# Username to use when constructing new comments
Username = "CountTheComments"

# Possible comment authors
Authors = ["authorA", "authorB"]

# Possible comments to count
Comments = [
    "Ram",
    "RAM",
    "rem",
    "I choose Felix!",
    "felis easily",
    "Emilia tan",
    "EMT",
    "Ram Rem",
    "Rem Ram",
    "Emilia Maji Tenshi Emilia Ram Rem",
    'Ram then rem in that order',
    "It'd have to be Felix i think",
    "I don't remember :(",
    "Emili Ram"
]

# Valid summons
SummonComments = [
    "u/CountTheComments Rem Ram Rem Ram Rem Ram Rem Ram",
    "u/CountTheComments Rem/Ram Rem/Emilia Emilia/Rem",
    "u/CountTheComments Rem/Ram Ram/Rem",
    "u/CountTheComments Rem/Ram Rem/Felix"
    "u/CountTheComments Rem Ram Felix/Felis Emilia/EMT",
    "u/CountTheComments Rem Felix / Felis Emilia /EMT",
    "u/CountTHeCOmments rem felix ff/ felis",
    "u/CountTHeCOmments rem felix ff /felis",
    "u/CountTheComments Rem Ram Felix/Felis Emilia/EMT/E.M.T/Emilia Maji Tenshi",
    "Can we get u/CountTheComments Rem Ram in here?",
    " u/CountTheComments Rem Ram Felix",
    "u/countthecomments rem ram felix",
    "u/COUNTTHECOMMENTS rem Ram",
    "/u/COuntTheComments Rem Ram Felix",
    "/u/COuntTheComments Rem                    Ram   Felix",
    "/u/CountTHeComments term1  term2 term3.. term4",
    "/u/CountTHeComments term1  term2 term3..",
    "/u/CountTHeComments term1  term2 term3 skiddybumpimdoo..",
]

# Valid mentions, but incorrectly formatted terms
InvalidSummonComments = [
    "u/CountTheComments",
    "u/CountTheComments ... Ram Felix",
    "u/CountTheComments ...Ram Felix",
    "/u/CountTheComments",
    "test and then u/Countthecomments",
    "test and then /u/CountTheComments"
]

# Invalid mentions (in inbox due to comment replies)
ReplyComments = [
    "u/CountTheComments... Ram Felix",
    "u/CounteTheComments&one&two",
    "test/u/CountTheComments rem ram",
    "u/countthecommentsrem ram",
    "Uhhhhu/CountTheComments Rem Ram",
    "CountTHeComments marker1 marker2"
]

# All comments that will arrive in inbox
InboxComments = SummonComments + InvalidSummonComments + ReplyComments