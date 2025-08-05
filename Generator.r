library(ggplot2)
library(dplyr)
library(scales)

set.seed(42)

# Parameters
n_users <- 50
n_weeks <- 12
lambda_symptom <- 2
rate_first_completion <- 1 / 6    # mean = 6 min
rate_followup_completion <- 1 / 3 # mean = 3 min

records <- data.frame(UserID = integer(), 
                      Week = numeric(), 
                      CompletionTimeMin = numeric())

# Simulate reports
for (user_id in 1:n_users) {
  repeat {
    n_symptoms <- rpois(1, lambda_symptom)
    if (n_symptoms > 0) break
  }
  
  report_times <- sort(runif(n_symptoms, 0, n_weeks))
  
  for (i in seq_along(report_times)) {
    completion <- if (i == 1) {
      rexp(1, rate = rate_first_completion)
    } else {
      rexp(1, rate = rate_followup_completion)
    }
    
    records <- rbind(records, data.frame(
      UserID = user_id,
      Week = report_times[i],
      CompletionTimeMin = completion
    ))
  }
}

# Tag first reports
records <- records %>%
  arrange(UserID, Week) %>%
  group_by(UserID) %>%
  mutate(
    Shape = ifelse(row_number() == 1, "First Report", "Symptom Report")
  ) %>%
  ungroup()

# Email reminder logic: every 4 weeks if no report in last 2 weeks
reminder_weeks <- seq(4, n_weeks, by = 4)
reminder_df <- data.frame()

for (uid in unique(records$UserID)) {
  user_data <- records %>% filter(UserID == uid) %>% arrange(Week)
  if (nrow(user_data) == 0) next
  
  first_report <- min(user_data$Week)
  
  for (remind_time in reminder_weeks) {
    # Only check reminders AFTER registration
    if (remind_time >= (first_report + 2)) {
      # Hasn't reported in last 2 weeks before this reminder
      if (all(user_data$Week < (remind_time - 2) | user_data$Week > remind_time)) {
        reminder_df <- rbind(reminder_df, data.frame(
          UserID = uid,
          Week = remind_time,
          CompletionTimeMin = NA,
          Shape = "Reminder"
        ))
      }
    }
  }
}


# Combine all data
final_df <- bind_rows(records, reminder_df)
final_df$Shape <- factor(final_df$Shape, levels = c("First Report", "Symptom Report", "Reminder"))

# Cap completion time at 15 min for color mapping
final_df$CappedCompletion <- pmin(final_df$CompletionTimeMin, 15)

# Ordering data
first_report_order <- final_df %>%
  filter(Shape == "First Report") %>%
  arrange(Week) %>%
  pull(UserID)

# Create an ordered factor for UserID
final_df$UserID <- factor(final_df$UserID, levels = unique(first_report_order))

# Plot
ggplot(final_df, aes(x = Week, y = factor(UserID))) +
  geom_vline(xintercept = 0, color = "black", linewidth = 1.2)+
  geom_segment(aes(x = 0, xend = n_weeks, y = factor(UserID), yend = factor(UserID)),
               color = "black", size = 0.6, alpha = 0.6)+
  geom_point(aes(
    shape = Shape,
    fill = CappedCompletion
  ),
  size = 3,
  color = "black") +
  scale_shape_manual(
    values = c("First Report" = 22, "Symptom Report" = 21, "Reminder" = 24),
    name = "Event Type"
  ) +
  scale_fill_gradient(
    low = "green", high = "red", na.value = "white",
    limits = c(0, 15),
    name = "Completion\nTime (min)"
  ) +
  scale_x_continuous(breaks = seq(0, 12, 2)) +
  labs(
    title = "Symptom Reporting Timeline with Reminders",
    x = "Weeks",
    y = "Individual"
  ) +
  theme_minimal() +
  theme(axis.text.y = element_blank(),
        axis.ticks.y = element_blank())