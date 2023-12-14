import pygame
pygame.font.init()


class TextInput:
    def __init__(self, 
                 x:int|float, 
                 y:int|float, 
                 width:int|float, 
                 height:int|float, 
                 curr_text:str = "", 
                 placeholder:str = "", 
                 font:pygame.font.Font = pygame.font.Font(None, 10), 
                 background_color:tuple = (255,255,255), 
                 outline_color:tuple = (0,0,0),
                 outline_width:int = 0,
                 text_color:tuple = (0, 0, 0)
                ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.curr_text = curr_text
        self.pointer = 0
        self.position_shift = 0
        self.placeholder = placeholder
        self.font = font
        self.background_color = background_color
        self.active_background_color = background_color
        self.inactive_background_color = background_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.text_color = text_color

        self.text_surface = font.render(self.curr_text, True, text_color)

        self.active = False

        self.submit_action = None
        self.submit_do_default = True

        self.pressing_down = None
        self.pressing_down_time = 0


    
    def handle_event(self, events:list, dt:float) -> bool:
        '''Called at the start of every game loop'''
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if self.active:
                #Check key presses
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.on_submit()
                        continue
                    elif event.key == pygame.K_BACKSPACE:
                        if self.pointer == 0:
                            continue
                        self.curr_text = self.curr_text[0:self.pointer-1] + self.curr_text[self.pointer:]
                        self.pointer -= 1
                    elif event.key == pygame.K_LEFT:
                        if self.pointer > 0:
                            self.pointer -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.pointer < len(self.curr_text):
                            self.pointer += 1
                    else:
                        self.curr_text = self.curr_text[0:self.pointer] + event.unicode + self.curr_text[self.pointer:]
                        self.pointer += 1
                    
                    self.pressing_down = event
                    self.pressing_down_time = 0
                
                
                
                if event.type == pygame.KEYUP:
                    if self.pressing_down and event.key == self.pressing_down.key:
                        self.pressing_down = None
                        self.pressing_down_time = 0
        
        #Key hold down actions
        if self.pressing_down_time > 0.5:
            if self.pressing_down.key == pygame.K_BACKSPACE:
                if self.pointer > 0:
                    self.curr_text = self.curr_text[0:self.pointer-1] + self.curr_text[self.pointer:]
                    self.pointer -= 1
            elif self.pressing_down.key == pygame.K_LEFT:
                if self.pointer > 0:
                    self.pointer -= 1
            elif self.pressing_down.key == pygame.K_RIGHT:
                if self.pointer < len(self.curr_text):
                    self.pointer += 1
            else:
                self.curr_text += self.pressing_down.unicode
                self.pointer += 1
            self.pressing_down_time -= 0.1
        
        if self.pressing_down:
            self.pressing_down_time += dt
        
        #display surface creating
        if self.active:
            text_render = self.font.render(self.curr_text, True, self.text_color)
            
            text_surface_width = text_render.get_width()
            text_width_right_of_pointer = self.font.render(self.curr_text[self.pointer:], True, self.text_color).get_width()
            pointer_loc = text_surface_width - text_width_right_of_pointer
            pointer_surface = pygame.Surface((self.font.get_height()//10,self.font.get_height()))
            pointer_surface.fill(self.text_color)

            if pointer_loc - self.position_shift + pointer_surface.get_width() > self.width - 10:
                self.position_shift = pointer_loc + pointer_surface.get_width() - self.width + 10

            elif pointer_loc < self.position_shift and text_width_right_of_pointer > self.width:
                self.position_shift = pointer_loc
            
            elif pointer_loc - self.position_shift + text_width_right_of_pointer < self.width - 10 - pointer_surface.get_width():
                self.position_shift = 0 if pointer_loc + pointer_surface.get_width() - self.width + 10 < 0 else pointer_loc+ pointer_surface.get_width() - self.width + 10
            
            self.text_surface = pygame.Surface((text_render.get_width()+pointer_surface.get_width(), text_render.get_height()), pygame.SRCALPHA, 32)
            self.text_surface.convert_alpha()
            self.text_surface.blit(pointer_surface, (pointer_loc-pointer_surface.get_width()*0.5, 0))
            self.text_surface.blit(text_render, (0, 0))

        elif self.curr_text:
            self.text_surface = self.font.render(self.curr_text, True, self.text_color)
            
        else:
            self.text_surface = self.font.render(self.placeholder, True, (100, 100, 100, 100))
            
            

    def set_active_background_color(self, color:tuple):
        self.active_background_color = color
    
    def set_inactive_background_color(self, color:tuple):
        self.inactive_background_color = color
    
    
    def set_on_submit(self, func, do_default:bool = True):
        '''Set action when return is pressed
        
        Parameters
        ----------
        func
            Function to be called, take in 1 argument: self
        do_default
            Whether to clear text and set inactive or not
        '''
        self.submit_action = func
        self.submit_do_default = do_default
        
    def on_submit(self):
        if self.submit_action:
            self.submit_action(self)
        if not self.submit_do_default:
            return
        
        self.pointer = 0
        self.curr_text = ""
        self.active = False
    
    def draw(self, screen:pygame.Surface):
        self.background_color = self.active_background_color if self.active else self.inactive_background_color
        pygame.draw.rect(screen, self.background_color, self.rect)
        pygame.draw.rect(screen, self.outline_color, (self.rect.x-self.outline_width, self.rect.y-self.outline_width, self.rect.width+self.outline_width*2, self.rect.height+self.outline_width*2), self.outline_width)
        display_surface = pygame.Surface((self.rect.width-10, self.rect.height-10))
        display_surface.fill(self.background_color)
        display_surface.blit(self.text_surface, (-self.position_shift, 0))
        screen.blit(display_surface, (self.rect.x + 5, self.rect.y + 5))


    def __dict__(self) -> dict:
        return









