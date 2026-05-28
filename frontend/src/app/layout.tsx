import "./globals.css";
import React from "react";
import type { Metadata } from "next";
import Providers from "./providers";
import ThemeToggle from "./theme-toggle";
import { withBasePath } from "@/lib/path";

export const metadata: Metadata = {
  title: "Career Advisor | AI 진로 추천",
  description: "생기부와 공공데이터를 결합해 학생에게 알맞은 전공과 직무를 추천하는 AI 서비스입니다.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" data-theme="light">
      <body>
        <Providers>
          <div className="flex min-h-screen flex-col">
            <header className="sticky top-0 z-50 border-b backdrop-blur-md bg-white/75 dark:bg-[#060913]/75" style={{ borderColor: "var(--line)" }}>
              <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
                <div className="flex items-center gap-3">
                  <span className="h-3 w-3 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-400 shadow-md shadow-indigo-500/50" />
                  <a href={withBasePath("/")} className="text-xl font-extrabold tracking-tight">
                    CAREER <span className="bg-gradient-to-r from-indigo-500 to-cyan-500 bg-clip-text text-transparent">ADVISOR</span>
                  </a>
                </div>
                <nav className="flex items-center gap-4 text-sm font-semibold">
                  <a href={withBasePath("/upload")} className="hover:text-indigo-500 transition-colors">
                    분석 시작
                  </a>
                  <a href={withBasePath("/compare")} className="hover:text-indigo-500 transition-colors">
                    시나리오 비교
                  </a>
                  <ThemeToggle />
                </nav>
              </div>
            </header>

            <main className="mx-auto w-full max-w-7xl flex-grow animate-fade-in px-4 py-8 sm:px-6 lg:px-8">
              {children}
            </main>

            <footer className="border-t py-6 text-center text-xs text-muted" style={{ borderColor: "var(--line)" }}>
              <p>2026 Career Advisor AI. All rights reserved. Powered by Public Big Data & LLM Agent.</p>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}
