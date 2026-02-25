import type {Metadata} from "next";
import {Geist, Geist_Mono} from "next/font/google";
import "./globals.css";
import ThemeProvider from "@/providers/ThemeProvider"
import {AppProvider} from "@/providers/AppProvider";

import {
    SidebarInset,
    SidebarProvider,
} from "@/components/ui/sidebar"

import AppSidebar from "@/app/_layout/AppSidebar";
import SiteHeader from "@/app/_layout/SideHeader";
import Spinner from "@/components/general/Spinner";
import { Toaster } from "sonner"

const geistSans = Geist({
    variable: "--font-geist-sans",
    subsets: ["latin"],
});

const geistMono = Geist_Mono({
    variable: "--font-geist-mono",
    subsets: ["latin"],
});

export const metadata: Metadata = {
    title: "ASL Method Section Generator",
    description: "Generate ASL Method Sections with ease",
};

export default function RootLayout({
                                       children,
                                   }: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
        <body
            className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        >
        <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
        >
            <AppProvider>
                <SidebarProvider
                    style={
                        {
                            "--sidebar-width": "calc(var(--spacing) * 72)",
                            "--header-height": "calc(var(--spacing) * 12)",
                        } as React.CSSProperties
                    }
                >
                    <AppSidebar variant="inset"/>
                    <SidebarInset>
                        <SiteHeader/>
                        <Spinner/>
                        <Toaster  position="bottom-right" richColors />
                        {children}
                    </SidebarInset>

                </SidebarProvider>
            </AppProvider>
        </ThemeProvider>
        </body>
        </html>
    );
}
