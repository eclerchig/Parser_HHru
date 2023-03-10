from django.db import models


# Create your models here.
class Vacancies(models.Model):
    name_vac = models.CharField("Название вакансии", max_length=100, default='')
    url_hh = models.CharField("Ссылка на вакансию", max_length=100, default='')

    def __str__(self):
        return self.name_vac

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'


class Skills(models.Model):
    vacancy = models.ForeignKey('Vacancies', on_delete=models.CASCADE, null=True)
    name_skill = models.CharField("Название навыка", max_length=100)

    def __str__(self):
        return self.name_skill

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
