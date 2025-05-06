library(tidymodels)
library(kknn)
library(dplyr)
library(doParallel)
library(foreach)

# Load data
model_data_50d_noNA <- readRDS("~/PROJECT/RDS_files/model_data_50d_noNA.rds")

# Split data
set.seed(999)
data_split <- initial_split(model_data_50d_noNA, prop = 0.995)
train_data <- training(data_split)
test_data <- testing(data_split)

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
    step_zv(all_predictors()) %>%
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
  knn_test_preds <- predict(knn_fit, new_data = test_data) %>%
    bind_cols(test_data %>% select(Return_50d))
  end_time <- Sys.time()
  
  # Save predictions
  filename <- paste0("~/PROJECT/model_preds/kNN_old/knn_test_predictions_", format(n, scientific = FALSE), ".rds")
  saveRDS(knn_test_preds, filename)
  
  # Save timing info
  timing_info <- paste("Sample size:", n, "\nElapsed time:", round(difftime(end_time, start_time, units = "mins"), 2), "minutes")
  log_filename <- paste0("~/PROJECT/runtime_analysis/kNN_old/knn_model_log_", format(n, scientific = FALSE), ".txt")
  writeLines(timing_info, log_filename)
}

stopCluster(cl)
message("All tasks complete.")
