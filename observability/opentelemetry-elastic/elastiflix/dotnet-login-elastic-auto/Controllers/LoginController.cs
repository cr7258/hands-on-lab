using System;
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using Serilog;

namespace login.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class LoginController : ControllerBase
    {
        private static readonly List<string> UserNames = new List<string>
        {
            "Alice",
            "Bob",
            "Charlie",
            "Dave",
            "Eva"
        };

        // Responds to GET requests.
        [HttpGet]
        public ActionResult Get()
        {
            var user = GenerateRandomUserResponse();
            Log.Information("User logged in: {UserName}", user);
            return user;
        }

        // Responds to POST requests.
        [HttpPost]
        public ActionResult Post([FromBody] dynamic body)
        {
            // This is just an example, you might want to do something with the posted data.
            var user = GenerateRandomUserResponse();
            Log.Information("User logged in: {UserName}", user);
            return user;
        }

        private ActionResult GenerateRandomUserResponse()
        {
            var random = new Random();
            var index = random.Next(UserNames.Count);
            return Ok(new { userName = UserNames[index] });
        }
    }
}
