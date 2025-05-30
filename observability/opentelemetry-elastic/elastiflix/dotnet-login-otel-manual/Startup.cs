using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;
using OpenTelemetry;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using Elastic.CommonSchema.Serilog;
using Elastic.Apm.SerilogEnricher;
using OpenTelemetry.Exporter;
using System.Net.Http.Headers;


// Define some important constants and the activity source.
// These can come from a config file, constants file, etc.


namespace UserService
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
             Configuration = configuration;
        }

        public IConfiguration Configuration { get; }
        public void ConfigureServices(IServiceCollection services)
        {

            services.AddOpenTelemetry().WithTracing(builder => builder.AddOtlpExporter()
                                .AddSource("Login")
                                .AddAspNetCoreInstrumentation()
                                .AddOtlpExporter()  
                    .ConfigureResource(resource =>
                        resource.AddService(
                            serviceName: "Login"))
            );

            services.AddControllers();

        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            app.UseRouting();

            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
            });
                        
        }
}
}
