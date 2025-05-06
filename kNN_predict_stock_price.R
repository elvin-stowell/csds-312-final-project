library(tidymodels)
library(kknn)
library(dplyr)
library(doParallel)
library(foreach)

# Load data
model_data_50d_noNA <- readRDS("~/PROJECT/RDS_files/model_data_50d_noNA.rds")

# Ticker-aware split (1% test for speed)
set.seed(42)
tickers <- unique(model_data_50d_noNA$Ticker)
test_tickers <- sample(tickers, size = floor(0.002 * length(tickers)))
test_data <- model_data_50d_noNA %>% filter(Ticker %in% test_tickers)
train_data <- model_data_50d_noNA %>% filter(!Ticker %in% test_tickers)

# Sample sizes
sample_sizes <- c(10000)

# Set up parallel backend
n_cores <- parallel::detectCores(logical = FALSE)
cl <- makeCluster(n_cores)
registerDoParallel(cl)

# Parallel loop
foreach(n = sample_sizes, .packages = c("tidymodels", "kknn", "dplyr")) %dopar% {
  set.seed(124)
  train_subset <- train_data %>% slice_sample(n = n)
  
  # Recipe
  knn_rec <- recipe(Return_50d ~ ., data = train_subset) %>%
    update_role(Ticker, Date, new_role = "id") %>%
    step_zv(all_predictors()) %>%
    step_mutate(SMA_Cross = as.integer(SMA_Cross)) %>% 
    step_normalize(all_numeric_predictors())
  
  # Model
  knn_mod <- nearest_neighbor(neighbors = 5, weight_func = "rectangular") %>%
    set_engine("kknn") %>%
    set_mode("regression")
  
  # Workflow
  knn_wf <- workflow() %>%
    add_model(knn_mod) %>%
    add_recipe(knn_rec)
  
  # Fit and predict
  start_time <- Sys.time()
  knn_fit <- fit(knn_wf, data = train_subset)
  
  # Ensure preprocessing is applied to test data
  test_processed <- bake(prep(knn_rec), new_data = test_data)
  
  # Predict
  knn_preds <- predict(knn_fit, new_data = test_processed)
  
  if (nrow(knn_preds) == nrow(test_data)) {
    knn_test_preds <- bind_cols(knn_preds, test_data %>% select(Ticker, Date, Return_50d))
    
    # Save predictions
    filename <- paste0("~/PROJECT/model_preds/kNN_new/knn_test_predictions_", format(n, scientific = FALSE), ".rds")
    saveRDS(knn_test_preds, filename)
  } else {
    warning(paste("Prediction failed or row mismatch for sample size", n))
  }
  
  # Save timing info
  end_time <- Sys.time()
  duration <- round(difftime(end_time, start_time, units = "mins"), 2)
  timing_info <- paste("Sample size:", n, "\nElapsed time:", duration, "minutes")
  log_filename <- paste0("~/PROJECT/runtime_analysis/kNN_new/knn_model_log_", format(n, scientific = FALSE), ".txt")
  writeLines(timing_info, log_filename)
}

stopCluster(cl)
message("All tasks complete.")