package configs

import (
	"fmt"
	"log"
	"os"
)

func EnvMongoURI() string {
	err := os.Getenv("MONGO_URI")
	if err == "" {
		log.Fatal("MONGO_URI not found in .env file")
	}

	fmt.Println("MONGO_URI found in .env file")

	return os.Getenv("MONGO_URI")
}
