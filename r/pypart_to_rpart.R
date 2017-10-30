##########
# Converts the CSV output of a pypart function call to an rpart object
# to allow the usage of native rpart functions with pypart trees
##########
pyPartToRpart <- function(frameCSV, cpTableCSV, whereCSV, splitsCSV, method="anova", ...) {
    
    # contains information about each node
    frame <- read.csv(frameCSV, header=TRUE, row.names=1)
    
    # cp table
    cpTable <- read.csv(cpTableCSV, header=TRUE, row.names=1)
    cpTable <- as.matrix(cpTable)
    
    # where each row in the origincal dataset ends up (which terminal node)
    whereDf <- read.csv(whereCSV, header=TRUE)
    where = whereDf$node
    names(where) <- whereDf$name
    
    Call = c()      # a copy of the rpart function call "rpart(...)"
    Terms = c()
    method = method # Anova, Gini, Poisson, User
    parms = c()     # not sure, is null on rpart cars.csv tree
    controls = c()   # values from rpart.control
    functions = c() # spits out some weird functions for rpart cars.csv tree
    numresp = 1   # I believe this is the number of classes for the tree (1 for regression trees)
    
    tree <- list(frame = frame,
                where = where,
                call = Call, 
                terms = Terms,
                cptable = cpTable,
                method = method,
                parms = parms,
                control = controls,
                functions = functions,
                numresp = numresp)
    
    # information on all of the splits
    splits <- read.csv(splitsCSV, header=TRUE)
    tree$splits <- as.matrix(splits[,-1])
    rownames(tree$splits) <- splits$name
    
    # fool other functions into thinking this is an rpart tree
    attr(tree, "class") <- "rpart"
    return(tree)
}