using System;
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using Serilog;
using System.Diagnostics;
using OpenTelemetry;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using OpenTelemetry.Exporter;
using OpenTelemetry;
using OpenTelemetry.Exporter;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

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

            using (Activity activity = Telemetry.LoginActivitySource.StartActivity("SomeWork"))
            {
                var user = GenerateRandomUserResponse();
                Log.Information("User logged in: {UserName}", user);
                return user;
            }


            
        }

        // Responds to POST requests.
        [HttpPost]
        public ActionResult Post([FromBody] dynamic body)
        {

            using (Activity activity = Telemetry.LoginActivitySource.StartActivity("SomeWork"))
            {
                var user = GenerateRandomUserResponse();
                Log.Information("User logged in: {UserName}", user);
                return user;
            }
        }

        private ActionResult GenerateRandomUserResponse()
        {
            var random = new Random();
            var index = random.Next(UserNames.Count);
            return Ok(new { userName = UserNames[index] });
        }
    }
}
