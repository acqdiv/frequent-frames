# Functions for analyzing frequent frames data
# Steven Moran <steven.moran@uzh.ch>

library(rjson)
library(xtable)
library(ggplot2)
library(dplyr)
library(reshape2)


# Common graph theme elements
common_theme <- 
  theme(text = element_text(family = 'CMU Sans Serif')) +
  theme_grey() +
  # theme(axis.title=element_text(size=14, face='bold')) +
  theme(axis.title=element_text(size=18)) +
  theme(plot.title = element_text(size = 24, face = "bold")) +
  theme(strip.text = element_text(size=24)) + 
+ theme(legend.text=element_text(size=24))
+ theme(legend.title=element_text(size=24))
+ axis.text.x = element_text(size=42)
# theme(element_text=(legend.text='none'))
theme_set(common_theme)

PlotOperationalization <- function(df, n, title, filename)  {
  # Plot operationalization example: x axis threshold frequency, y axis log # of FFs
  df <- df %>% select(Corpus, NumberFrames, frequency)
  p <- ggplot(df, aes(x=frequency, y=NumberFrames)) +
    geom_point(aes(color = Corpus)) +
    xlab('Relative frequency of frame') +
    ylab('Number of frame tokens')
    # + geom_vline(xintercept = .001)
  ggsave(filename=filename)
  p
}

PlotPr <- function(df, title, filename, yscale) {
  # Plot the PR values and get statistic summaries
  p <- ggplot(df, aes(x=Precision, y=Recall)) + 
    facet_wrap(~Corpus, nrow = 2) + 
    geom_point(aes(size = NumberFrames)) + 
    scale_size_continuous(range = c(1, 5)) +
    scale_x_continuous(limits=c(0, 1)) +
    scale_y_continuous(limits=c(0, yscale)) +
    # xlab("Precision") +
    # ylab("Recall") +
    xlab("Accuracy") +
    ylab("Completeness") +
    labs(size="Frequency") +
    # ggtitle(title)
    ggsave(filename=filename)
  p
}

TableSummary <- function(df, filename, cap, lab) {
  # Remove the more accurate bigrams
  y <- df %>% filter(W1_PrecisionGreater==FALSE) %>% filter(W1_PrecisionGreater==FALSE)
  # Don't remove the more accurate bigrams
  # y <- df
  # Continue
  z <- as.data.frame(summary(y$Corpus))
  colnames(z) <- "Frames"
  z$Precision <- tapply(y$Precision, y$Corpus, mean)
  z$SD.Precision <- tapply(y$Precision, y$Corpus, sd)
  z$Recall <- tapply(y$Recall, y$Corpus, mean)  
  z$SD.Recall <- tapply(y$Recall, y$Corpus, sd)
  z$Frames2 <- z$Frames
  z$Frames <- NULL
  z$Min <- tapply(y$NumberFrames, y$Corpus, min)
  z$Max <- tapply(y$NumberFrames, y$Corpus, max)
  z$Median <- tapply(y$NumberFrames, y$Corpus, median)
  xtable(z)
  # names(z) <- c('Precision', 'SD', 'Recall', 'SD', 'Frames', 'Min', 'Max', 'Median')
  names(z) <- c('Accuracy', 'SD', 'Completeness', 'SD', 'Frames', 'Min', 'Max', 'Median')
  # filename <- file.path(path.out, paste(n, "summary-per-corpus.tex", sep="-"))
  print(xtable(z, caption=cap, label=lab), type="latex", file=filename)
  print(z)
}

TableSummaryGlobal <- function(df, filename, cap, lab)  {
  rownames(df) <- NULL
  names(df) <- c('Corpus', 'POS', 'Accuracy', 'Completeness', 'Frames')
  df <- df %>% arrange(POS, Corpus)
  print(xtable(df, caption=cap, label=lab), type="latex", file=filename)
  print(df)
}

PlotGlobalRecall <- function(df, title, filename, yscale)  {
  if(missing(yscale)) {
    yscale <- 1
    } 
  # Plot the mean average precison vs global recall
  p <- ggplot(df, aes(x=average.precision, y=global.recall)) + 
    facet_wrap(~Corpus, nrow = 2) + 
    geom_point(aes(size = frame.count, color = ModalCategory)) + 
    scale_size_continuous(range = c(1, 5)) +
    scale_x_continuous(limits=c(0, 1)) +
    scale_y_continuous(limits=c(0, yscale)) +
    # xlab("Global precison") +
    # ylab("Global recall") +
    xlab("Global accuracy") +
    ylab("Global completeness") +
    labs(color = "POS", size="Frequency")# +
    # ggtitle(title)
  ggsave(p, filename=filename)
  p
}

PlotCounts <- function(df, filename){
  # Plot number of utterances, trigrams, bigrams
  df$count <- NULL
  m <- melt(df) # raw numbers
  p <- ggplot(data=m, aes(x=corpus, y=value, fill=variable)) +
    geom_bar(stat="identity", position=position_dodge(), colour="black") +
    xlab("Corpus") +
    ylab("Count")
  ggsave(filename=filename)
  p
}

TableAccuracy <- function(df, path.out, n, cap, lab) {
  # Create latex table of bigram accuray
  w1 <- as.data.frame(table(df$Corpus, df$W1_PrecisionGreater))
  w2 <- as.data.frame(table(df$Corpus, df$W2_PrecisionGreater))
  colnames(w1) <- c("Corpus", "value", "freq")
  colnames(w2) <- c("Corpus", "value", "freq")
  w1.split <- split(w1, w1$value)
  w2.split <- split(w2, w2$value)
  w1 <- cbind(w1.split[[1]], w1.split[[2]])
  w2 <- cbind(w2.split[[1]], w2.split[[2]])
  colnames(w1) <- c("Corpus", "value.1", "W1_false", "corpus.2", "value.2", "W1_true")
  colnames(w2) <- c("Corpus", "value.1", "W2_false", "corpus.2", "value.2", "W2_true")
  w1$value.1 <- NULL
  w1$corpus.2 <- NULL
  w1$value.2 <- NULL
  w2$value.1 <- NULL
  w2$corpus.2 <- NULL
  w2$value.2 <- NULL
  w1$W1 <- w1$W1_true / (w1$W1_true + w1$W1_false)
  w2$W2 <- w2$W2_true / (w2$W2_true + w2$W2_false)
  x <- cbind(w1, w2)
  x$W1_false <- NULL
  x$W2_false <- NULL
  x$W1_true <- NULL
  x$W2_true <- NULL
  colnames(x) <- c("Corpus", "AB", "corpus.2", "BC")
  x$corpus.2 <- NULL
  # Create latex table
  filename <- file.path(path.out, paste(n, "bigram-frequency.tex", sep="-"))
  print(xtable(x, caption=cap, label=lab), type="latex", file=filename)
  print(x)
}

PlotAccuracy<-function(df, path.out, n) {
  x <- as.data.frame(table(df$Corpus, df$W1_PrecisionGreater))
  x$word <- as.factor("W1")
  y <- as.data.frame(table(df$Corpus, df$W2_PrecisionGreater))
  y$word <- as.factor("W2")
  z <- rbind(x,y)
  colnames(z) <- c('Corpus', 'FreqGreater', 'Frequency', 'Position')
  # Plot corpus results in facet
  p <- ggplot(data=z, aes(x=Position, y=Frequency, group=Corpus, fill=FreqGreater)) +
    geom_bar(stat="identity") +
    labs(fill="More accurate", x="Bigrams") +
    facet_wrap(~ Corpus) 
  output <- file.path(path.out, paste(n, "bigram-frequency.pdf", sep = "-"))
  ggsave(filename=output)
}


# For recall and global recall
GlossesToDf <- function(json) {
  # This function takes a list of json representations and transforms
  # them into an unrolled data frame, preserving record ids
  #  
  # input: a character vector of json lists wehre each element is in 
  #        format like "[{label: sfx, form: a}, {label: sfx, form: a}]"
  #        every element in the vector represents one record
  # 
  # output: a data frame with columns record.i, word.i, label, form
  
  # make sure that json is a character vector
  json <- as.character(json)
  # parse each entry of the json vector as an individual record
  # we use a global variable to ensure every word i is unique
  .word_offset <- 0 # the global offset for the next word id
  records <- lapply(json, function(json_record) {
    words <- fromJSON(json_record)
    # validate the entries
    for(word in words) {
      valid <- identical(names(word), c('form', 'label'))
      if(!valid) stop('Expected {"label":"value", "form":"value"}, got', toJSON(word))
    }
    words <- data.frame(word.i = seq_along(words) + .word_offset, do.call(rbind, lapply(words, function(vals) {
      vals[sapply(vals, is.null)] <- NA
      vals
    })))
    .word_offset <<- max(words$word.i)
    words$label <- unlist(words$label)
    words$form <- unlist(words$form)
    
    words
  })
  
  # make the records into a data frame
  for(i in seq_along(records)) { records[[i]] <- data.frame(record.i = i, records[[i]]) }
  records <- do.call(rbind, records)
  records
}

GetGlossesTable <- function(df)  {
  # Extract glosses table from ff data
  glosses <- df %>%
    group_by(Corpus) %>% 
    do({
      gl <- GlossesToDf(.$Targets)
      gl
    }) %>% 
    as.data.frame
  return(glosses)
}

GetRecall <- function(data, glosses)  {
  # Create table of newly caculated recall
  total.counts <- glosses %>% group_by(Corpus) %>% distinct(form, label) %>% summarize(all.target.types=n())
  row.counts <- glosses %>% group_by(Corpus, record.i) %>% distinct(form, label) %>% summarize(frame.target.types=n())
  row.counts$row.id <- as.integer(rownames(data))
  row.counts <- left_join(row.counts, total.counts)
  row.counts <- row.counts %>% mutate(Recall = frame.target.types/all.target.types)
  row.counts$Corpus <- NULL
  data$row.id <- as.integer(rownames(data))
  data$Targets <- NULL
  new.data <- left_join(data, row.counts, by="row.id")
  return(new.data)
}

GetGlobalRecall <- function(df)  {
  # Need description
  x <- df %>% select(Corpus, NumberFrames, Precision, ModalCategory)
  x.totals <- x %>% group_by(Corpus, ModalCategory) %>% summarize(total.frames = sum(NumberFrames))
  head(x.totals)
  x <- x %>% mutate(num.frame.precision=NumberFrames*Precision)
  y <- left_join(x, x.totals, by=c("Corpus"="Corpus", "ModalCategory"="ModalCategory"))
  z <- y %>% group_by(Corpus, ModalCategory) %>% summarize(sum.precision = sum(num.frame.precision))
  a <- left_join(z, x.totals)
  b <- a %>% mutate(average.precision=sum.precision/total.frames)
  return(b)
}

GetGlossCounts <- function(df)  {
  # Get glosses and glosses count table
  x <- df %>% select(Corpus, label, form) %>% group_by(Corpus, label) %>% distinct(form) %>% summarize(frame.count = n())
  x$label <- as.factor(x$label)
  return(x)
}

GetGlobalRecallTable <- function(glosses, types.counts, data) {
  # Needs description
  counts <- glosses %>% select(Corpus, label, form) %>% group_by(Corpus, label) %>% distinct(form) %>% summarize(frame.count = n())
  counts$label <- as.factor(counts$label)
  glimpse(counts)
  
  # Get global recall table
  global.recall <- left_join(counts, types.counts, by=c("Corpus"="corpus", "label"="pos"))
  global.recall <- global.recall %>% mutate(global.recall = frame.count/type.count)
  head(global.recall); dim(global.recall)
  # Here we need global recall
  words.global.recall <- GetGlobalRecall(data)
  head(words.global.recall)
  final <- left_join(words.global.recall,global.recall,by=c("Corpus"="Corpus", "ModalCategory"="label"))
  dim(final)
  head(final)
  final <- final %>% select(Corpus, ModalCategory, average.precision, global.recall, frame.count)
  head(final)
  df <- final  
}

# For cleaning
CleanJapanese <- function(df)  {
  # Rename Japanese
  levels(df$Corpus)[match("Japanese_MiiPro", levels(df$Corpus))] <- "Japanese"
  rownames(df) <- NULL
  df <- droplevels(df)
  return(df)
}

CleanCounts <- function(df) {
  # Counts long-to-wide format for processing
  l <- melt(df)
  df <- dcast(l, corpus~type)
  return(df)
}

# For operationalization
GetBetterBigrams <- function(df) {
  # Identify the bigrams with greater precision
  df$W1_PrecisionGreater <- df$Precision < df$W1_Precision
  df$W2_PrecisionGreater <- df$Precision < df$W2_Precision
  return(df)
}

RemoveBetterBigrams <- function(df) {
  # Remove the frames with better performing bigram constituents
  df <- df[df$W1_PrecisionGreater==FALSE, ]
  df <- df[df$W2_PrecisionGreater==FALSE, ]
  return(df)
}

GetFortyFive <- function(df) {
  # Return the 45 most frequent frames
  x <- df %>% group_by(Corpus) %>% arrange(desc(NumberFrames)) %>% top_n(n=45, wt=NumberFrames)
  return(x %>% group_by(Corpus) %>% slice(1:45))
}

GetTop10 <- function(df) {
  # Return the top 10 most frequent frames
  x <- df %>% group_by(Corpus) %>% arrange(desc(NumberFrames)) %>% top_n(n=10, wt=NumberFrames) %>% select(Corpus, Precision, NumberFrames, Frame, ModalCategory, TargetTokens)
  return(x %>% group_by(Corpus) %>% slice(1:10))
}

Operationalize <- function(df, count) {
  # Operationalize by relative proportion per corpus
  df$frequency<-(-1)
  lgs<-as.character(unique(df$Corpus))
  for(i in 1:length(lgs)) {print(c(lgs[i],count[i]));df$frequency[as.character(df$Corpus)==lgs[i]]<-df$NumberFrames[as.character(df$Corpus)==lgs[i]]/count[i]}
  return(df)
}



