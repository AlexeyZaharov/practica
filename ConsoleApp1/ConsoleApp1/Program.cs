using System;
using System.Collections.Generic;
using System.Text;
using System.IO;
using EAGetMail; // add EAGetMail namespace

using System.Reflection;
using System.Security.Permissions;

public static class Resolver
{
    private static volatile bool _loaded;

    public static void RegisterDependencyResolver()
    {
        if (!_loaded)
        {
            AppDomain.CurrentDomain.AssemblyResolve += OnResolve;
            _loaded = true;
        }
    }

    private static Assembly OnResolve(object sender, ResolveEventArgs args)
    {
        Assembly execAssembly = Assembly.GetExecutingAssembly();
        string resourceName = String.Format("{0}.{1}.dll",
            execAssembly.GetName().Name,
            new AssemblyName(args.Name).Name);

        using (var stream = execAssembly.GetManifestResourceStream(resourceName))
        {
            int read = 0, toRead = (int)stream.Length;
            byte[] data = new byte[toRead];

            do
            {
                int n = stream.Read(data, read, data.Length - read);
                toRead -= n;
                read += n;
            } while (toRead > 0);

            return Assembly.Load(data);
        }
    }
}

namespace receiveemail
{
    class Program
    {

        static Program()
        {
            Resolver.RegisterDependencyResolver();
        }

        static void Main(string[] args)
        {
            Console.WriteLine("Hello, I'm is a pop3-client for outlook-mailbox (pop3.live.com).\n");

            // Hotmail/MSN POP3 server is "pop3.live.com"
            Console.WriteLine("Your login:");
            string login = Console.ReadLine();

            Console.WriteLine("\nYour password:");
            string password = Console.ReadLine();

            MailServer oServer = new MailServer("pop3.live.com",
                        login, password, ServerProtocol.Pop3);
            MailClient oClient = new MailClient("TryIt");

            // Set SSL connection
            oServer.SSLConnection = true;

            // Set 995 SSL port
            oServer.Port = 995;

            try
            {
                oClient.Connect(oServer);
                MailInfo[] infos = oClient.GetMailInfos();
                for (int i = 0; i < infos.Length; i++)
                {
                    MailInfo info = infos[i];
                    Console.WriteLine("Index: {0}; Size: {1}; UIDL: {2}",
                        info.Index, info.Size, info.UIDL);

                    // Download email from Hotmail/MSN POP3 server
                    Mail oMail = oClient.GetMail(info);

                    Console.WriteLine("From: {0}", oMail.From.ToString());
                    Console.WriteLine("Subject: {0}\r\n", oMail.Subject);

                    if ( (i+1) % 5  == 0)
                    {
                        Console.WriteLine("\n\nGet next 5 letter? [y/n]");
                        string next = Console.ReadLine();
                        if (next == "y")
                        {
                            continue;
                        }
                        else
                        {
                            break;
                        }
                    }
                }

                // Quit and purge emails marked as deleted from Hotmail/MSN Live server.
                oClient.Quit();
                Console.WriteLine("\n\nGoodbye");
                Console.ReadLine();
            }
            catch (Exception ep)
            {
                Console.WriteLine(ep.Message);
                Console.ReadLine();
            }

        }
    }
}