db.createUser(
	{
		user: "loop_dev",
		pwd: "loop_dev",
		roles: [
			{ 
				role: "dbAdmin", 
				db: "loop_dev" 
			},
			{ 
				role: "readWrite", 
				db: "loop_dev" 
			},
		]
	}
)
