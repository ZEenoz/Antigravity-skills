#!/usr/bin/env bash
set -euo pipefail

if [ -f "pom.xml" ]; then
  echo "Detected Maven project"
  mvn clean test
  echo "To run JavaFX app, try: mvn javafx:run"
elif [ -f "gradlew" ]; then
  echo "Detected Gradle wrapper"
  ./gradlew clean test
  echo "To run JavaFX app, try: ./gradlew run"
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
  echo "Detected Gradle project"
  gradle clean test
  echo "To run JavaFX app, try: gradle run"
else
  echo "No Maven/Gradle build file detected. Please configure build/run commands."
  exit 1
fi
