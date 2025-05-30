using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;
//using Serilog.Formatting.Compact;
using Elastic.CommonSchema.Serilog;
using Elastic.Apm.SerilogEnricher;


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
        services.AddControllers();
    }

    public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
    {
        if (env.IsDevelopment())
        {
            app.UseDeveloperExceptionPage();
        }

        // app.UseHttpsRedirection();

        Log.Logger = new LoggerConfiguration()
              .Enrich.WithElasticApmCorrelationInfo()
              .Enrich.WithProperty("metadata_event_dataset", "cartService.log")
              .WriteTo.Console(new EcsTextFormatter()).CreateLogger();

        app.UseRouting();

        app.UseAuthorization();

        app.UseEndpoints(endpoints =>
        {
             endpoints.MapControllers();
        });
    }
}
}
