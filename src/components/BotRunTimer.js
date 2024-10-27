import React, { useEffect, useState } from "react";
import moment from "moment-timezone";
import { Card, CardContent, Typography, Box } from "@mui/material";

const BotRunTimer = () => {
  const [timeLeft, setTimeLeft] = useState("");

  // Check if today is a weekend and adjust to the next Monday
  const getNextMarketDay = (date) => {
    const day = date.day(); // 0 is Sunday, 6 is Saturday, 5 is Friday
    if (day === 6) {
      // If it's Saturday, move to Monday
      return date.add(2, "days");
    } else if (day === 0) {
      // If it's Sunday, move to Monday
      return date.add(1, "day");
    } else if (day === 5 && date.isAfter(moment.tz("America/New_York").set({ hour: 10, minute: 15, second: 0 }))) {
      // If it's Friday after 10:15 AM, move to Monday
      return date.add(3, "days");
    }
    return date;
  };

  // Calculate the time difference for the next bot run at 10:15 AM US/Eastern
  const calculateTimeLeft = () => {
    const currentTime = moment();
    let nextBotRun = moment.tz("America/New_York").set({ hour: 10, minute: 15, second: 0 });

    // If the current time is past 10:15 AM today, set the next run to tomorrow
    if (currentTime.isAfter(nextBotRun)) {
      nextBotRun = nextBotRun.add(1, "day");
    }

    // Ensure the next run is on a market day (Monday to Friday)
    nextBotRun = getNextMarketDay(nextBotRun);

    // Calculate the difference between the current time and the next bot run time
    const difference = moment.duration(nextBotRun.diff(currentTime));

    return {
      hours: difference.hours(),
      minutes: difference.minutes(),
      seconds: difference.seconds(),
    };
  };

  useEffect(() => {
    // Update the timer every second
    const timer = setInterval(() => {
      const timeLeft = calculateTimeLeft();
      setTimeLeft(`${timeLeft.hours}h ${timeLeft.minutes}m ${timeLeft.seconds}s`);
    }, 1000);

    // Cleanup the timer when the component is unmounted
    return () => clearInterval(timer);
  }, []);

  return (
    <Box display="flex" marginRight={7}>
      <Card sx={{ width: 225, height: 160, textAlign: "center", backgroundColor: "#1e1e1e", borderRadius: '4px',border: '2px solid #333333'}}>
        <CardContent>
          <Typography variant="h6" component="div" sx={{ fontWeight: "bold", color: "#f0a500" }} gutterBottom>
            NEXT RUN
          </Typography>
          <Typography variant="subtitle1" sx={{ fontWeight: "bold", marginTop: 0.5, marginBottom: 0.5, color: "#f0a500" }}>
            {timeLeft}
          </Typography>
          <Typography variant="body2" sx={{ textSizeAdjust: "20%", color: "#e0e0e0" }}>
            This Bot Is Scheduled To Run Monday-Friday At 10:15 AM US/Eastern
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default BotRunTimer;
