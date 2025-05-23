"use client"

import { useState } from "react"
import Link from "next/link"
import { motion } from "framer-motion"
import { Github, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"

interface ProjectCardProps {
  title: string
  description: string
  tags: string[]
  githubUrl: string
  demoUrl: string
}

export default function ProjectCard({ title, description, tags, githubUrl, demoUrl }: ProjectCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      viewport={{ once: true }}
    >
      <Card
        className="h-full overflow-hidden transition-all duration-300 hover:shadow-lg"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{title}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">{description}</p>
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <Badge key={tag} variant="secondary">
                {tag}
              </Badge>
            ))}
          </div>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline" size="sm" asChild>
            <Link href={githubUrl} target="_blank">
              <Github className="mr-2 h-4 w-4" />
              Code
            </Link>
          </Button>
          <Button size="sm" asChild>
            <Link href={demoUrl} target="_blank">
              <ExternalLink className="mr-2 h-4 w-4" />
              Demo
            </Link>
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  )
}