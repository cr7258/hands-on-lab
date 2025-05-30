using System;
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using Serilog;
using Elastic.Apm;

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

            var transaction = Elastic.Apm.Agent.Tracer.StartTransaction("MyTransaction","Request");
            try
            {
                var user = GenerateRandomUserResponse();
                Log.Information("User logged in: {UserName}", user);
                return user;
            }
            catch (Exception e)
            {
                transaction.CaptureException(e);
                throw;
            }
            finally
            {
                transaction.End();
            }   

        }

        // Responds to POST requests.
        [HttpPost]
        public ActionResult Post([FromBody] dynamic body)
        {
            var transaction = Elastic.Apm.Agent.Tracer.StartTransaction("MyTransaction", "Request");
            try
            {
                var user = GenerateRandomUserResponse();
                Log.Information("User logged in: {UserName}", user);
                return user;
            }
            catch (Exception e)
            {
                transaction.CaptureException(e);
                throw;
            }
            finally
            {
                transaction.End();
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
