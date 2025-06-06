"use client"

import React from "react"
import Link from "next/link"
import { Github, Linkedin, Mail } from 'lucide-react'
import { Button } from "../components/ui/button"
import { ThemeToggle } from "../components/theme-toggle"
import ProjectCard from "../components/project-card"
import SkillBadge from "../components/skill-badge"
import AnimatedSection from "../components/animated-section"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="font-bold text-xl">
            <span className="text-primary">Jerin</span>Mulangan
          </Link>
          <nav className="flex items-center gap-6">
            <Link href="#about" className="text-sm font-medium hover:text-primary transition-colors">
              About
            </Link>
            <Link href="#skills" className="text-sm font-medium hover:text-primary transition-colors">
              Skills
            </Link>
            <Link href="#projects" className="text-sm font-medium hover:text-primary transition-colors">
              Projects
            </Link>
            <ThemeToggle />
          </nav>
        </div>
      </header>

      <main className="container py-10 space-y-24">
        <AnimatedSection className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] text-center space-y-4">
          <h1 className="text-4xl font-bold sm:text-5xl md:text-6xl">
            Hi, I&apos;m <span className="text-primary">Jerin Mulangan</span>
          </h1>
          <p className="max-w-[42rem] text-muted-foreground sm:text-xl">
            Software Engineer specializing in building efficient full stack systems and data analysis algorithms
          </p>
          <div className="flex gap-4 mt-6">
            <Button asChild>
              <Link href="#projects">View Projects</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/resume.pdf" target="_blank" rel="noopener noreferrer">
                Resume
              </Link>
            </Button>
          </div>
        </AnimatedSection>

        <AnimatedSection id="about" className="space-y-6">
          <h2 className="text-3xl font-bold tracking-tight">About Me</h2>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              <p>
                I&apos;m a software engineer with a strong full-stack foundation and a growing focus on AI and machine learning.
                I enjoy building modern web applications that not only scale but also integrate intelligent features to 
                enhance user experience and decision-making.
              </p>
              <p>
                Over the past 5 years, I&apos;ve worked on a range of projects, from full-stack systems to interactive data 
                visualizations, where I've applied both engineering best practices and data-driven insights. Recently, my 
                interests have expanded into building and evaluating ML models, integrating them into real-world applications, 
                and exploring how AI can solve practical problems at scale.
              </p>
              <p>
                When I&apos;m not coding, I spend time producing music and editing videos, creative outlets that challenge me to think
                in new ways and stay sharp with both technical and artistic tools. I&apos;m always experimenting, whether it&apos;s tuning a 
                neural network or a synth patch.
              </p>
            </div>
            <div className="bg-muted rounded-lg p-6 flex flex-col justify-center">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Mail className="h-5 w-5 text-primary" />
                  <Link href="mailto:jerinmulangan@outlook.com" className="hover:text-primary transition-colors">
                    jerinmulangan@outlook.com
                  </Link>
                </div>
                <div className="flex items-center gap-2">
                  <Github className="h-5 w-5 text-primary" />
                  <Link
                    href="https://github.com/jerinmulangan"
                    target="_blank"
                    className="hover:text-primary transition-colors"
                  >
                    github.com/jerinmulangan
                  </Link>
                </div>
                <div className="flex items-center gap-2">
                  <Linkedin className="h-5 w-5 text-primary" />
                  <Link
                    href="https://www.linkedin.com/in/jerinmulangan/"
                    target="_blank"
                    className="hover:text-primary transition-colors"
                  >
                    linkedin.com/in/jerinmulangan
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </AnimatedSection>

        <AnimatedSection id="skills" className="space-y-6">
          <h2 className="text-3xl font-bold tracking-tight">Skills</h2>
          <div className="space-y-6">
            <div className="space-y-3">
              <h3 className="text-xl font-semibold">Frontend</h3>
              <div className="flex flex-wrap gap-2">
                <SkillBadge name="React" />
                <SkillBadge name="Next.js" />
                <SkillBadge name="TypeScript" />
                <SkillBadge name="Tailwind CSS" />
                <SkillBadge name="JavaScript (ES6+)" />
                <SkillBadge name="HTML5/CSS3" />
                <SkillBadge name="Bootstrap" />
                <SkillBadge name="ESLint" />
              </div>
            </div>
            <div className="space-y-3">
              <h3 className="text-xl font-semibold">Backend</h3>
              <div className="flex flex-wrap gap-2">
                <SkillBadge name="Python" />
                <SkillBadge name="Node.js" />
                <SkillBadge name="Express.js" />
                <SkillBadge name="Java/Springboot" />
                <SkillBadge name="C# ASP.NET" />
                <SkillBadge name="C/C++" />
                <SkillBadge name="Django" />
                <SkillBadge name="PostgreSQL" />
                <SkillBadge name="MySQL" />
                <SkillBadge name="MongoDB" />
              </div>
            </div>
            <div className="space-y-3">
              <h3 className="text-xl font-semibold">Tools & Others</h3>
              <div className="flex flex-wrap gap-2">
                <SkillBadge name="Git" />
                <SkillBadge name="Docker" />
                <SkillBadge name="AWS" />
                <SkillBadge name="CI/CD" />
                <SkillBadge name="Jest" />
                <SkillBadge name="JUnit" />
                <SkillBadge name="Pytest" />
                <SkillBadge name="Figma" />
              </div>
            </div>
          </div>
        </AnimatedSection>

        <AnimatedSection id="projects" className="space-y-6">
          <h2 className="text-3xl font-bold tracking-tight">Projects</h2>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <ProjectCard
              title="E-commerce Platform"
              description="A full-stack e-commerce platform with payment integration, user authentication, and admin dashboard."
              tags={["Next.js", "Node.js", "MongoDB", "Stripe"]}
              githubUrl="https://github.com/johndoe/ecommerce"
              demoUrl="https://ecommerce-demo.com"
            />
            <ProjectCard
              title="Data Visualization Tool"
              description="An interactive dashboard for visualizing complex datasets with filtering and export capabilities."
              tags={["React", "D3.js", "Express", "PostgreSQL"]}
              githubUrl="https://github.com/johndoe/data-viz"
              demoUrl="https://data-viz-demo.com"
            />
            <ProjectCard
              title="Task Management App"
              description="A collaborative task management application with real-time updates and team features."
              tags={["React", "Firebase", "Tailwind CSS"]}
              githubUrl="https://github.com/johndoe/task-app"
              demoUrl="https://task-app-demo.com"
            />
            <ProjectCard
              title="Weather Forecast App"
              description="A weather application that provides accurate forecasts using multiple weather APIs."
              tags={["JavaScript", "OpenWeather API", "Chart.js"]}
              githubUrl="https://github.com/johndoe/weather-app"
              demoUrl="https://weather-app-demo.com"
            />
            <ProjectCard
              title="Dijkstra Algorithm Visualizer"
              description="Real‑time Dijkstra visualizer in C++/SFML."
              tags={["C++", "SFML Framework", "Python"]}
              githubUrl="https://github.com/jerinmulangan/dir/tree/main/personal_projects/visual_dijkstra"
              demoUrl="https://github.com/jerinmulangan/dir/tree/main/personal_projects/visual_dijkstra"
            />
            <ProjectCard
              title="Portfolio Website"
              description="This portfolio website showcasing my projects and skills."
              tags={["Next.js", "TypeScript", "Framer Motion"]}
              githubUrl="https://github.com/jerinmulangan/dir/tree/main/personal_projects/personal_website"
              demoUrl="#"
            />
          </div>
        </AnimatedSection>
      </main>

      <footer className="border-t">
        <div className="container py-8 flex flex-col md:flex-row items-center justify-between">
          <p className="text-sm text-muted-foreground">© {new Date().getFullYear()} Jerin Mulangan. All rights reserved.</p>
          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <Link href="https://github.com/jerinmulangan" target="_blank" aria-label="GitHub">
              <Github className="h-5 w-5 hover:text-primary transition-colors" />
            </Link>
            <Link href="https://linkedin.com/in/jerinmulangan" target="_blank" aria-label="LinkedIn">
              <Linkedin className="h-5 w-5 hover:text-primary transition-colors" />
            </Link>
            <Link href="mailto:jerinmulangan@outlook.com" aria-label="Email">
              <Mail className="h-5 w-5 hover:text-primary transition-colors" />
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}